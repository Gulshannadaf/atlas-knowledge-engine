"""Document schemas."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class DocumentStatus(str, Enum):
    """Document processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentCreate(BaseModel):
    """Document creation schema (metadata only, file is separate)."""

    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentResponse(BaseSchema):
    """Document response schema."""

    id: str
    filename: str
    file_type: str
    file_size: int
    status: DocumentStatus
    error_message: str | None = None
    chunk_count: int
    metadata: dict[str, Any]
    created_at: datetime
    processed_at: datetime | None = None


class DocumentListResponse(BaseModel):
    """Document list response."""

    documents: list[DocumentResponse]
    total: int


class ChunkResponse(BaseSchema):
    """Chunk response schema."""

    id: str
    document_id: str
    content: str
    chunk_index: int
    token_count: int
    metadata: dict[str, Any]


class DocumentUploadResponse(BaseModel):
    """Document upload response."""

    id: str
    filename: str
    status: DocumentStatus
    message: str
