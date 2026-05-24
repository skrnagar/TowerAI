"""Celery tasks for alert generation and notification."""

from app.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)

VIOLATION_MESSAGES = {
    "helmet_off": "Worker detected without safety helmet",
    "harness_off": "Worker detected without safety harness",
    "restricted_zone": "Worker entered restricted zone",
}


@celery_app.task(name="app.tasks.alerts.process_violation", bind=True, max_retries=3)
def process_violation(self, violation_data: dict) -> dict:
    """
    Process a new violation:
    1. Create alert record in database
    2. Push real-time notification via Redis pub/sub
    3. Store screenshot reference in MinIO
    """
    logger.info("processing_violation", violation_type=violation_data.get("violation_type"))
    # Implementation in Step 13 — Alert System
    return {"status": "queued", "violation_id": violation_data.get("id")}


@celery_app.task(name="app.tasks.alerts.broadcast_alert")
def broadcast_alert(alert_data: dict) -> None:
    """Push alert to all connected WebSocket clients via Redis pub/sub."""
    logger.info("broadcasting_alert", alert_id=alert_data.get("id"))
    # Implementation in Step 11 — WebSocket streaming
