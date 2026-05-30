"""Celery application configuration."""

from celery import Celery

from app.config import settings

celery_app = Celery(
    "atlas",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=600,  # 10 minutes
    task_soft_time_limit=540,  # 9 minutes

    # Worker settings
    worker_prefetch_multiplier=1,
    worker_concurrency=2,

    # Result backend settings
    result_expires=3600,  # 1 hour

    # Task routing
    task_routes={
        "app.workers.tasks.process_document_task": {"queue": "documents"},
        "app.workers.tasks.run_evaluation_task": {"queue": "evaluations"},
    },

    # Default queue
    task_default_queue="default",
)
