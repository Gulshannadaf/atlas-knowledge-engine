"""Evaluation schemas."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class EvaluationStatus(str, Enum):
    """Evaluation run status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EvaluationCreate(BaseModel):
    """Evaluation creation request."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    dataset_path: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class EvaluationResponse(BaseSchema):
    """Evaluation response schema."""

    id: str
    name: str
    description: str | None
    status: EvaluationStatus
    metrics: dict[str, Any]
    created_at: datetime
    completed_at: datetime | None


class EvaluationResultResponse(BaseSchema):
    """Individual evaluation result."""

    id: str
    evaluation_id: str
    query: str
    expected_answer: str | None
    actual_answer: str
    contexts: list[str]
    metrics: dict[str, Any]
    created_at: datetime


class MetricsResponse(BaseModel):
    """Aggregated metrics response."""

    context_precision: float = Field(ge=0, le=1)
    context_recall: float = Field(ge=0, le=1)
    faithfulness: float = Field(ge=0, le=1)
    answer_relevancy: float = Field(ge=0, le=1)
    total_queries: int
    average_latency_ms: float
    average_cost_usd: float


class EvaluationListResponse(BaseModel):
    """Evaluation list response."""

    evaluations: list[EvaluationResponse]
    total: int
