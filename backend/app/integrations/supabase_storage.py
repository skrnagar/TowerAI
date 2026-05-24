"""Upload violation screenshots to Supabase Storage (when service role is configured)."""

from __future__ import annotations

import uuid
from typing import Optional

import httpx
import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)


def _configured() -> bool:
    s = get_settings()
    return bool(s.supabase_url and s.supabase_service_role_key)


async def upload_violation_screenshot(
    data: bytes,
    content_type: str = "image/jpeg",
    extension: str = "jpg",
) -> Optional[str]:
    """
    Upload bytes to violation-screenshots bucket.
    Returns storage object path (screenshot_key) or None if Supabase is not configured.
    """
    if not _configured():
        return None

    settings = get_settings()
    object_path = f"{uuid.uuid4()}.{extension}"
    url = (
        f"{settings.supabase_url.rstrip('/')}/storage/v1/object/"
        f"{settings.supabase_bucket_violations}/{object_path}"
    )
    headers = {
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": content_type,
        "x-upsert": "true",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, content=data, headers=headers)
        if resp.status_code not in (200, 201):
            logger.warning("supabase_storage_upload_failed", status=resp.status_code, body=resp.text)
            return None

    return object_path


def public_screenshot_url(screenshot_key: str) -> Optional[str]:
    """Signed URLs require a separate call; return path for backend-stored reference."""
    if not screenshot_key or not _configured():
        return None
    settings = get_settings()
    return (
        f"{settings.supabase_url.rstrip('/')}/storage/v1/object/"
        f"{settings.supabase_bucket_violations}/{screenshot_key}"
    )
