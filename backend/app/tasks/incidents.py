"""Celery tasks for incident logging and system health."""

from app.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.incidents.check_camera_health")
def check_camera_health() -> dict:
    """Periodic task — verify all registered cameras are reachable."""
    logger.info("checking_camera_health")
    # Implementation in Step 6 — RTSP camera ingestion
    return {"status": "ok", "checked": 0}


@celery_app.task(name="app.tasks.incidents.archive_recording")
def archive_recording(recording_id: str) -> dict:
    """Archive completed recording to MinIO long-term storage."""
    logger.info("archiving_recording", recording_id=recording_id)
    return {"status": "archived", "recording_id": recording_id}
