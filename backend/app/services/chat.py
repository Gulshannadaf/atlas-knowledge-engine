"""Chat service - placeholder for Phase 1 implementation."""

from typing import AsyncGenerator

import structlog

from app.models.database import Message
from app.schemas.chat import ChatResponse, Citation, StreamChunk

logger = structlog.get_logger()


class ChatService:
    """
    Chat service for generating responses.

    This is a placeholder that will be fully implemented in Phase 1-3.
    """

    async def generate_response(
        self,
        query: str,
        user_id: str,
        history: list[Message] | None = None,
    ) -> ChatResponse:
        """
        Generate a response for the given query.

        This will be implemented with:
        - Phase 1: Basic RAG with vector search
        - Phase 2: Hybrid search with reranking
        - Phase 3: LangGraph agent with tools
        """
        # Placeholder response
        logger.info("Generating response", query=query[:50], user_id=user_id)

        return ChatResponse(
            conversation_id="",  # Will be set by the route
            message_id="",  # Will be set by the route
            content=(
                "This is a placeholder response. The full RAG pipeline will be "
                "implemented in Phase 1. Upload some documents and try again!"
            ),
            citations=[],
            token_count=50,
            metadata={"phase": "0", "status": "placeholder"},
        )

    async def generate_response_stream(
        self,
        query: str,
        user_id: str,
        history: list[Message] | None = None,
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Generate a streaming response.

        Will be implemented in Phase 1-3.
        """
        logger.info("Generating streaming response", query=query[:50], user_id=user_id)

        # Placeholder streaming response
        words = [
            "This",
            "is",
            "a",
            "placeholder",
            "streaming",
            "response.",
            "The",
            "full",
            "implementation",
            "comes",
            "in",
            "Phase",
            "1.",
        ]

        for i, word in enumerate(words):
            yield StreamChunk(
                content=word + " ",
                done=i == len(words) - 1,
                citations=[] if i < len(words) - 1 else [],
            )
