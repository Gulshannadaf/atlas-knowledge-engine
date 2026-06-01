"""Evaluation endpoints."""

import structlog
from fastapi import APIRouter, HTTPException, status

from app.dependencies import CurrentUser, DatabaseDep
from app.repositories.evaluation import EvaluationRepository
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationListResponse,
    EvaluationResponse,
    EvaluationResultResponse,
    MetricsResponse,
)
from app.workers.tasks import run_evaluation_task

router = APIRouter()
logger = structlog.get_logger()


@router.post("", response_model=EvaluationResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_evaluation(
    request: EvaluationCreate,
    current_user: CurrentUser,
    db: DatabaseDep,
) -> EvaluationResponse:
    """
    Create and queue an evaluation run.

    The evaluation will be processed asynchronously.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can run evaluations",
        )

    eval_repo = EvaluationRepository(db)

    evaluation = await eval_repo.create(
        name=request.name,
        description=request.description,
        dataset_path=request.dataset_path,
        config=request.config,
    )

    # Queue evaluation task
    run_evaluation_task.delay(evaluation.id)

    logger.info(
        "Evaluation created",
        evaluation_id=evaluation.id,
        name=request.name,
    )

    return EvaluationResponse.model_validate(evaluation)


@router.get("", response_model=EvaluationListResponse)
async def list_evaluations(
    current_user: CurrentUser,
    db: DatabaseDep,
    limit: int = 50,
    offset: int = 0,
) -> EvaluationListResponse:
    """List all evaluations."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view evaluations",
        )

    eval_repo = EvaluationRepository(db)

    evaluations, total = await eval_repo.list(limit=limit, offset=offset)

    return EvaluationListResponse(
        evaluations=[EvaluationResponse.model_validate(e) for e in evaluations],
        total=total,
    )


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: str,
    current_user: CurrentUser,
    db: DatabaseDep,
) -> EvaluationResponse:
    """Get a specific evaluation by ID."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view evaluations",
        )

    eval_repo = EvaluationRepository(db)

    evaluation = await eval_repo.get_by_id(evaluation_id)

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )

    return EvaluationResponse.model_validate(evaluation)


@router.get("/{evaluation_id}/results", response_model=list[EvaluationResultResponse])
async def get_evaluation_results(
    evaluation_id: str,
    current_user: CurrentUser,
    db: DatabaseDep,
    limit: int = 100,
    offset: int = 0,
) -> list[EvaluationResultResponse]:
    """Get results for a specific evaluation."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view evaluations",
        )

    eval_repo = EvaluationRepository(db)

    evaluation = await eval_repo.get_by_id(evaluation_id)

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )

    results = await eval_repo.get_results(evaluation_id, limit=limit, offset=offset)

    return [EvaluationResultResponse.model_validate(r) for r in results]


@router.get("/metrics/latest", response_model=MetricsResponse)
async def get_latest_metrics(
    current_user: CurrentUser,
    db: DatabaseDep,
) -> MetricsResponse:
    """Get metrics from the most recent completed evaluation."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view evaluations",
        )

    eval_repo = EvaluationRepository(db)

    evaluation = await eval_repo.get_latest_completed()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No completed evaluations found",
        )

    metrics = evaluation.metrics

    return MetricsResponse(
        context_precision=metrics.get("context_precision", 0),
        context_recall=metrics.get("context_recall", 0),
        faithfulness=metrics.get("faithfulness", 0),
        answer_relevancy=metrics.get("answer_relevancy", 0),
        total_queries=metrics.get("total_queries", 0),
        average_latency_ms=metrics.get("average_latency_ms", 0),
        average_cost_usd=metrics.get("average_cost_usd", 0),
    )
