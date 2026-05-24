"""Celery application for async task processing."""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "towerai",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.alerts", "app.tasks.incidents"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "check-camera-health": {
            "task": "app.tasks.incidents.check_camera_health",
            "schedule": 60.0,
        },
    },
)
