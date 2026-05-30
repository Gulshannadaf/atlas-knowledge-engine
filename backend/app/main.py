"""
Atlas - AI Codebase Knowledge Assistant

Main FastAPI application entry point.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from app.api.middleware.logging import LoggingMiddleware
from app.api.middleware.rate_limit import RateLimitMiddleware
from app.api.routes import auth, chat, documents, evaluation, health
from app.config import settings
from app.db.session import close_db, init_db
from app.observability.logging import setup_logging
from app.services.vectordb import init_qdrant

# Initialize structured logging
setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    logger.info(
        "Starting Atlas",
        version=settings.app_version,
        environment=settings.environment,
    )

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Initialize Qdrant collection
    await init_qdrant()
    logger.info("Qdrant initialized")

    yield

    # Shutdown
    logger.info("Shutting down Atlas")
    await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="AI Codebase Knowledge Assistant - Production-grade RAG system",
        version=settings.app_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # ==========================================================================
    # Middleware (order matters - last added = first executed)
    # ==========================================================================

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limiting
    app.add_middleware(RateLimitMiddleware)

    # Request logging
    app.add_middleware(LoggingMiddleware)

    # ==========================================================================
    # Routes
    # ==========================================================================

    # Health checks (no prefix, no auth)
    app.include_router(health.router, tags=["Health"])

    # API routes
    api_prefix = "/api/v1"
    app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["Authentication"])
    app.include_router(documents.router, prefix=f"{api_prefix}/documents", tags=["Documents"])
    app.include_router(chat.router, prefix=f"{api_prefix}/chat", tags=["Chat"])
    app.include_router(evaluation.router, prefix=f"{api_prefix}/evaluation", tags=["Evaluation"])

    # ==========================================================================
    # Prometheus Metrics
    # ==========================================================================
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    # ==========================================================================
    # Exception Handlers
    # ==========================================================================

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Global exception handler for unhandled errors."""
        logger.exception(
            "Unhandled exception",
            path=request.url.path,
            method=request.method,
            error=str(exc),
        )

        if settings.debug:
            return JSONResponse(
                status_code=500,
                content={
                    "detail": str(exc),
                    "type": type(exc).__name__,
                },
            )

        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
