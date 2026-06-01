"""Health check endpoints."""

import structlog
from fastapi import APIRouter, Response
from redis import Redis

from app.config import settings
from app.db.session import engine
from app.schemas.common import HealthResponse
from app.services.vectordb import get_qdrant_client

router = APIRouter()
logger = structlog.get_logger()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns the health status of the application and its dependencies.
    """
    services: dict = {}

    # Check PostgreSQL
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        services["postgres"] = {"status": "healthy"}
    except Exception as e:
        services["postgres"] = {"status": "unhealthy", "error": str(e)}

    # Check Redis
    try:
        redis = Redis.from_url(settings.redis_url)
        redis.ping()
        services["redis"] = {"status": "healthy"}
    except Exception as e:
        services["redis"] = {"status": "unhealthy", "error": str(e)}

    # Check Qdrant
    try:
        client = get_qdrant_client()
        client.get_collections()
        services["qdrant"] = {"status": "healthy"}
    except Exception as e:
        services["qdrant"] = {"status": "unhealthy", "error": str(e)}

    # Determine overall status
    all_healthy = all(s.get("status") == "healthy" for s in services.values())
    status = "healthy" if all_healthy else "degraded"

    return HealthResponse(
        status=status,
        version=settings.app_version,
        environment=settings.environment,
        services=services,
    )


@router.get("/health/live")
async def liveness() -> Response:
    """Kubernetes liveness probe."""
    return Response(status_code=200)


@router.get("/health/ready")
async def readiness() -> Response:
    """Kubernetes readiness probe."""
    health = await health_check()
    if health.status == "healthy":
        return Response(status_code=200)
    return Response(status_code=503)
