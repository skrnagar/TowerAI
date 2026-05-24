"""Dashboard analytics API endpoints."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models import Alert, AlertStatus, Camera, CameraStatus, User, Violation, ViolationSeverity, ViolationType
from app.db.session import get_db
from app.schemas import DashboardStats, ViolationResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DashboardStats:
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    total_cameras = await db.scalar(select(func.count()).select_from(Camera).where(Camera.is_active == True))  # noqa: E712
    online_cameras = await db.scalar(
        select(func.count()).select_from(Camera).where(Camera.status == CameraStatus.ONLINE)
    )
    total_violations_today = await db.scalar(
        select(func.count()).select_from(Violation).where(Violation.created_at >= today_start)
    )
    critical_violations_today = await db.scalar(
        select(func.count())
        .select_from(Violation)
        .where(Violation.created_at >= today_start, Violation.severity == ViolationSeverity.CRITICAL)
    )
    pending_alerts = await db.scalar(
        select(func.count()).select_from(Alert).where(Alert.status == AlertStatus.PENDING)
    )

    violations_by_type: dict[str, int] = {}
    for vtype in ViolationType:
        count = await db.scalar(
            select(func.count())
            .select_from(Violation)
            .where(Violation.created_at >= today_start, Violation.violation_type == vtype)
        )
        violations_by_type[vtype.value] = count or 0

    recent_result = await db.execute(
        select(Violation).order_by(Violation.created_at.desc()).limit(10)
    )
    recent_violations = [
        ViolationResponse.model_validate(v) for v in recent_result.scalars().all()
    ]

    return DashboardStats(
        total_cameras=total_cameras or 0,
        online_cameras=online_cameras or 0,
        total_violations_today=total_violations_today or 0,
        critical_violations_today=critical_violations_today or 0,
        pending_alerts=pending_alerts or 0,
        violations_by_type=violations_by_type,
        recent_violations=recent_violations,
    )
