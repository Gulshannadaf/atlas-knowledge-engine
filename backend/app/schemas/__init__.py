"""Pydantic schemas for API request/response validation."""

from app.schemas.auth import (
    TokenResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentListResponse,
    DocumentStatus,
)
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    MessageResponse,
    ConversationResponse,
    Citation,
)
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationResponse,
    EvaluationResultResponse,
    MetricsResponse,
)
from app.schemas.common import (
    PaginatedResponse,
    ErrorResponse,
    HealthResponse,
)

__all__ = [
    # Auth
    "TokenResponse",
    "LoginRequest",
    "RegisterRequest",
    "UserResponse",
    # Document
    "DocumentCreate",
    "DocumentResponse",
    "DocumentListResponse",
    "DocumentStatus",
    # Chat
    "ChatRequest",
    "ChatResponse",
    "MessageResponse",
    "ConversationResponse",
    "Citation",
    # Evaluation
    "EvaluationCreate",
    "EvaluationResponse",
    "EvaluationResultResponse",
    "MetricsResponse",
    # Common
    "PaginatedResponse",
    "ErrorResponse",
    "HealthResponse",
]
