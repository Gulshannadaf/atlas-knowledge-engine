"""Pydantic schemas for API request/response validation."""

from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    Citation,
    ConversationResponse,
    MessageResponse,
)
from app.schemas.common import (
    ErrorResponse,
    HealthResponse,
    PaginatedResponse,
)
from app.schemas.document import (
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentStatus,
)
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationResponse,
    EvaluationResultResponse,
    MetricsResponse,
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
