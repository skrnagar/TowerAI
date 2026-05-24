"""Multi-channel alert notifications — WhatsApp, email, webhook (Blueprint v2.0)."""

import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


def send_whatsapp_alert(
    violation_type: str,
    camera_id: str,
    timestamp: str,
    screenshot_url: str,
    supervisor_phone: str | None = None,
) -> bool:
    """
    Send WhatsApp alert via Twilio Business API.
  Requires TWILIO_* env vars — disabled when not configured.
    """
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        logger.debug("whatsapp_skipped", reason="twilio_not_configured")
        return False

    phone = supervisor_phone or getattr(settings, "alert_supervisor_phone", "")
    if not phone:
        return False

    try:
        from twilio.rest import Client

        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        msg = (
            f"SAFETY ALERT | {violation_type.upper()} detected | "
            f"Camera: {camera_id} | Time: {timestamp} | Action required immediately!"
        )
        client.messages.create(
            from_=settings.twilio_whatsapp_from,
            to=f"whatsapp:{phone}",
            body=msg,
            media_url=[screenshot_url] if screenshot_url else None,
        )
        logger.info("whatsapp_sent", camera_id=camera_id, violation=violation_type)
        return True
    except Exception as e:
        logger.error("whatsapp_failed", error=str(e))
        return False


def send_webhook(url: str, payload: dict) -> bool:
    """POST violation payload to external ERP / incident system."""
    try:
        import httpx

        httpx.post(url, json=payload, timeout=10.0)
        return True
    except Exception as e:
        logger.error("webhook_failed", url=url, error=str(e))
        return False
