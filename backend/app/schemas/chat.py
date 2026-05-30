"""Chat schemas."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class MessageRole(StrEnum):
    """Message role enum."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Citation(BaseModel):
    """Citation schema for source references."""

    document_id: str
    document_name: str
    chunk_id: str
    content: str
    relevance_score: float = Field(ge=0, le=1)
    page: int | None = None
    section: str | None = None


class ChatRequest(BaseModel):
    """Chat request schema."""

    message: str = Field(min_length=1, max_length=10000)
    conversation_id: str | None = None
    include_sources: bool = True
    stream: bool = False


class ChatResponse(BaseModel):
    """Chat response schema."""

    conversation_id: str
    message_id: str
    content: str
    citations: list[Citation] = Field(default_factory=list)
    token_count: int | None = None
    latency_ms: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MessageResponse(BaseSchema):
    """Message response schema."""

    id: str
    conversation_id: str
    role: MessageRole
    content: str
    citations: list[Citation]
    token_count: int | None
    latency_ms: int | None
    created_at: datetime


class ConversationResponse(BaseSchema):
    """Conversation response schema."""

    id: str
    title: str | None
    message_count: int = 0
    created_at: datetime
    updated_at: datetime


class ConversationDetailResponse(ConversationResponse):
    """Conversation detail with messages."""

    messages: list[MessageResponse] = Field(default_factory=list)


class StreamChunk(BaseModel):
    """Streaming response chunk."""

    content: str
    done: bool = False
    citations: list[Citation] | None = None
    metadata: dict[str, Any] | None = None
