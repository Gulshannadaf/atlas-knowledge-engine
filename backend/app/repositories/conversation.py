"""Conversation repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Conversation
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """Repository for Conversation operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Conversation)

    async def create(self, user_id: str, title: str | None = None) -> Conversation:
        """Create a new conversation."""
        return await super().create(user_id=user_id, title=title)

    async def list_by_user(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Conversation]:
        """List conversations for a user."""
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())
