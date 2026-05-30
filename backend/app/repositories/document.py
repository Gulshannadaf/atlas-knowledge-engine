"""Document repository."""

from datetime import UTC

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Document, DocumentStatus
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Repository for Document operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Document)

    async def create(
        self,
        user_id: str,
        filename: str,
        file_type: str,
        file_size: int,
        file_path: str,
    ) -> Document:
        """Create a new document record."""
        return await super().create(
            user_id=user_id,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            file_path=file_path,
            status=DocumentStatus.PENDING,
        )

    async def list_by_user(
        self,
        user_id: str,
        status: DocumentStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Document], int]:
        """List documents for a user with optional status filter."""
        query = select(Document).where(Document.user_id == user_id)
        count_query = select(func.count()).select_from(Document).where(Document.user_id == user_id)

        if status:
            query = query.where(Document.status == status)
            count_query = count_query.where(Document.status == status)

        query = query.order_by(Document.created_at.desc()).offset(offset).limit(limit)

        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)

        return list(result.scalars().all()), count_result.scalar_one()

    async def update_status(
        self,
        document_id: str,
        status: DocumentStatus,
        error_message: str | None = None,
        chunk_count: int | None = None,
    ) -> Document | None:
        """Update document processing status."""
        update_data = {"status": status}

        if error_message is not None:
            update_data["error_message"] = error_message

        if chunk_count is not None:
            update_data["chunk_count"] = chunk_count

        if status == DocumentStatus.COMPLETED:
            from datetime import datetime
            update_data["processed_at"] = datetime.now(UTC)

        return await self.update(document_id, **update_data)
