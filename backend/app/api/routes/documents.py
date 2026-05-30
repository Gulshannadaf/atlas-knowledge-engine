"""Document management endpoints."""

import os
from uuid import uuid4

import structlog
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.config import settings
from app.dependencies import CurrentUser, DatabaseDep
from app.models.database import DocumentStatus
from app.repositories.document import DocumentRepository
from app.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
    DocumentUploadResponse,
)
from app.workers.tasks import process_document_task

router = APIRouter()
logger = structlog.get_logger()


def validate_file(file: UploadFile) -> tuple[str, str]:
    """Validate uploaded file and return (file_type, extension)."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    # Get extension
    _, ext = os.path.splitext(file.filename)
    ext = ext.lower()

    if ext not in settings.allowed_file_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {ext} not allowed. Allowed types: {settings.allowed_file_types}",
        )

    # Check file size (if available)
    if file.size and file.size > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB",
        )

    return ext, ext.lstrip(".")


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    current_user: CurrentUser,
    db: DatabaseDep,
    file: UploadFile = File(...),
) -> DocumentUploadResponse:
    """
    Upload a document for processing.

    The document will be queued for async processing (parsing, chunking, embedding).
    """
    ext, file_type = validate_file(file)

    # Generate unique filename
    file_id = str(uuid4())
    filename = file.filename or f"document{ext}"
    stored_filename = f"{file_id}{ext}"
    file_path = os.path.join(settings.upload_dir, stored_filename)

    # Ensure upload directory exists
    os.makedirs(settings.upload_dir, exist_ok=True)

    # Save file
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        file_size = len(content)
    except Exception as e:
        logger.exception("Failed to save uploaded file", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file",
        )

    # Create document record
    doc_repo = DocumentRepository(db)
    document = await doc_repo.create(
        user_id=current_user.id,
        filename=filename,
        file_type=file_type,
        file_size=file_size,
        file_path=file_path,
    )

    # Queue processing task
    process_document_task.delay(document.id)

    logger.info(
        "Document uploaded",
        document_id=document.id,
        filename=filename,
        file_type=file_type,
        file_size=file_size,
        user_id=current_user.id,
    )

    return DocumentUploadResponse(
        id=document.id,
        filename=filename,
        status=DocumentStatus.PENDING,
        message="Document queued for processing",
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    current_user: CurrentUser,
    db: DatabaseDep,
    status_filter: DocumentStatus | None = None,
    limit: int = 50,
    offset: int = 0,
) -> DocumentListResponse:
    """List all documents for the current user."""
    doc_repo = DocumentRepository(db)

    documents, total = await doc_repo.list_by_user(
        user_id=current_user.id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(doc) for doc in documents],
        total=total,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: CurrentUser,
    db: DatabaseDep,
) -> DocumentResponse:
    """Get a specific document by ID."""
    doc_repo = DocumentRepository(db)

    document = await doc_repo.get_by_id(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check ownership
    if document.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: CurrentUser,
    db: DatabaseDep,
) -> None:
    """Delete a document and its associated chunks/vectors."""
    doc_repo = DocumentRepository(db)

    document = await doc_repo.get_by_id(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check ownership
    if document.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Delete file from disk
    if os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
        except OSError:
            logger.warning("Failed to delete file", path=document.file_path)

    # Delete from database (cascades to chunks)
    await doc_repo.delete(document_id)

    # TODO: Delete vectors from Qdrant

    logger.info("Document deleted", document_id=document_id, user_id=current_user.id)
