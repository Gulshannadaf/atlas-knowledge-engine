"""Evaluation repository."""

from datetime import UTC
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Evaluation, EvaluationResult, EvaluationStatus
from app.repositories.base import BaseRepository


class EvaluationRepository(BaseRepository[Evaluation]):
    """Repository for Evaluation operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Evaluation)

    async def create(
        self,
        name: str,
        description: str | None = None,
        dataset_path: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> Evaluation:
        """Create a new evaluation."""
        return await super().create(
            name=name,
            description=description,
            dataset_path=dataset_path,
            config=config or {},
            status=EvaluationStatus.PENDING,
        )

    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Evaluation], int]:
        """List all evaluations."""
        query = (
            select(Evaluation).order_by(Evaluation.created_at.desc()).offset(offset).limit(limit)
        )
        count_query = select(func.count()).select_from(Evaluation)

        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)

        return list(result.scalars().all()), count_result.scalar_one()

    async def get_latest_completed(self) -> Evaluation | None:
        """Get the most recent completed evaluation."""
        result = await self.session.execute(
            select(Evaluation)
            .where(Evaluation.status == EvaluationStatus.COMPLETED)
            .order_by(Evaluation.completed_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        evaluation_id: str,
        status: EvaluationStatus,
        metrics: dict[str, Any] | None = None,
    ) -> Evaluation | None:
        """Update evaluation status."""
        update_data: dict[str, Any] = {"status": status}

        if metrics is not None:
            update_data["metrics"] = metrics

        if status == EvaluationStatus.COMPLETED:
            from datetime import datetime

            update_data["completed_at"] = datetime.now(UTC)

        return await self.update(evaluation_id, **update_data)

    async def add_result(
        self,
        evaluation_id: str,
        query: str,
        actual_answer: str,
        expected_answer: str | None = None,
        contexts: list[str] | None = None,
        metrics: dict[str, Any] | None = None,
    ) -> EvaluationResult:
        """Add a result to an evaluation."""
        result = EvaluationResult(
            evaluation_id=evaluation_id,
            query=query,
            expected_answer=expected_answer,
            actual_answer=actual_answer,
            contexts=contexts or [],
            metrics=metrics or {},
        )
        self.session.add(result)
        await self.session.flush()
        await self.session.refresh(result)
        return result

    async def get_results(
        self,
        evaluation_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[EvaluationResult]:
        """Get results for an evaluation."""
        result = await self.session.execute(
            select(EvaluationResult)
            .where(EvaluationResult.evaluation_id == evaluation_id)
            .order_by(EvaluationResult.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())
