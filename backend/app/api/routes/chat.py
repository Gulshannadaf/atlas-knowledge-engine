"""Chat endpoints."""

import time
from collections.abc import AsyncGenerator

import structlog
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.dependencies import CurrentUser, DatabaseDep
from app.repositories.conversation import ConversationRepository
from app.repositories.message import MessageRepository
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationDetailResponse,
    ConversationResponse,
    MessageResponse,
)
from app.services.chat import ChatService

router = APIRouter()
logger = structlog.get_logger()


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: CurrentUser,
    db: DatabaseDep,
) -> ChatResponse | StreamingResponse:
    """
    Send a message and receive a response.

    If stream=true, returns a Server-Sent Events stream.
    """
    start_time = time.time()
    conv_repo = ConversationRepository(db)
    msg_repo = MessageRepository(db)
    chat_service = ChatService()

    # Get or create conversation
    if request.conversation_id:
        conversation = await conv_repo.get_by_id(request.conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
        if conversation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
    else:
        conversation = await conv_repo.create(user_id=current_user.id)

    # Get conversation history
    history = await msg_repo.get_by_conversation(conversation.id, limit=10)

    # Save user message
    await msg_repo.create(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )

    # Handle streaming response
    if request.stream:

        async def generate() -> AsyncGenerator[str, None]:
            async for chunk in chat_service.generate_response_stream(
                query=request.message,
                user_id=current_user.id,
                history=history,
            ):
                yield f"data: {chunk.model_dump_json()}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    # Generate response
    response = await chat_service.generate_response(
        query=request.message,
        user_id=current_user.id,
        history=history,
    )

    latency_ms = int((time.time() - start_time) * 1000)

    # Save assistant message
    assistant_message = await msg_repo.create(
        conversation_id=conversation.id,
        role="assistant",
        content=response.content,
        citations=[c.model_dump() for c in response.citations],
        token_count=response.token_count,
        latency_ms=latency_ms,
        cost_usd=response.metadata.get("cost_usd"),
    )

    # Update conversation title if first message
    if len(history) == 0:
        title = request.message[:50] + "..." if len(request.message) > 50 else request.message
        await conv_repo.update(conversation.id, title=title)

    logger.info(
        "Chat response generated",
        conversation_id=conversation.id,
        user_id=current_user.id,
        latency_ms=latency_ms,
        token_count=response.token_count,
    )

    return ChatResponse(
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        content=response.content,
        citations=response.citations,
        token_count=response.token_count,
        latency_ms=latency_ms,
        metadata=response.metadata,
    )


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    current_user: CurrentUser,
    db: DatabaseDep,
    limit: int = 50,
    offset: int = 0,
) -> list[ConversationResponse]:
    """List all conversations for the current user."""
    conv_repo = ConversationRepository(db)

    conversations = await conv_repo.list_by_user(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )

    return [ConversationResponse.model_validate(c) for c in conversations]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    current_user: CurrentUser,
    db: DatabaseDep,
) -> ConversationDetailResponse:
    """Get a conversation with all its messages."""
    conv_repo = ConversationRepository(db)
    msg_repo = MessageRepository(db)

    conversation = await conv_repo.get_by_id(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    messages = await msg_repo.get_by_conversation(conversation_id, limit=100)

    return ConversationDetailResponse(
        id=conversation.id,
        title=conversation.title,
        message_count=len(messages),
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[MessageResponse.model_validate(m) for m in messages],
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    current_user: CurrentUser,
    db: DatabaseDep,
) -> None:
    """Delete a conversation and all its messages."""
    conv_repo = ConversationRepository(db)

    conversation = await conv_repo.get_by_id(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    await conv_repo.delete(conversation_id)

    logger.info("Conversation deleted", conversation_id=conversation_id, user_id=current_user.id)
