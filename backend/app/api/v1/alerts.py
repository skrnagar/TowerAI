"""Alert management API endpoints."""

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.core.security import UserRole
from app.db.models import Alert, AlertStatus, User
from app.db.session import get_db
from app.schemas import AlertResponse, AlertUpdate, PaginatedResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=PaginatedResponse)
async def list_alerts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    severity: str | None = None,
) -> PaginatedResponse:
    query = select(Alert)
    if status_filter:
        query = query.where(Alert.status == AlertStatus(status_filter))
    if severity:
        query = query.where(Alert.severity == severity)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    result = await db.execute(
        query.order_by(Alert.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    alerts = result.scalars().all()

    return PaginatedResponse(
        items=[AlertResponse.model_validate(a) for a in alerts],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: UUID,
    data: AlertUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.OPERATOR))],
) -> AlertResponse:
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    if data.status:
        alert.status = AlertStatus(data.status)
        if data.status in ("resolved", "dismissed"):
            alert.resolved_by = current_user.id
            alert.resolved_at = datetime.now(timezone.utc)
    if data.resolution_note:
        alert.resolution_note = data.resolution_note

    await db.flush()
    await db.refresh(alert)
    return AlertResponse.model_validate(alert)
