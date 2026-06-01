"""Message repository."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Message, MessageRole
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """Repository for Message operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Message)

    async def create(
        self,
        conversation_id: str,
        role: str | MessageRole,
        content: str,
        citations: list[dict[str, Any]] | None = None,
        token_count: int | None = None,
        latency_ms: int | None = None,
        cost_usd: float | None = None,
    ) -> Message:
        """Create a new message."""
        if isinstance(role, str):
            role = MessageRole(role)

        return await super().create(
            conversation_id=conversation_id,
            role=role,
            content=content,
            citations=citations or [],
            token_count=token_count,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
        )

    async def get_by_conversation(
        self,
        conversation_id: str,
        limit: int = 100,
    ) -> list[Message]:
        """Get messages for a conversation, ordered by creation time."""
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())
