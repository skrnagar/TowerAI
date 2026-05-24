"""Violation management API endpoints."""

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.core.security import UserRole
from app.db.models import User, Violation, ViolationSeverity, ViolationType
from app.schemas import PaginatedResponse, ViolationCreate, ViolationResponse

router = APIRouter(prefix="/violations", tags=["Violations"])


@router.get("", response_model=PaginatedResponse)
async def list_violations(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    camera_id: UUID | None = None,
    site_id: UUID | None = None,
    violation_type: str | None = None,
    severity: str | None = None,
) -> PaginatedResponse:
    query = select(Violation)
    if camera_id:
        query = query.where(Violation.camera_id == camera_id)
    if site_id:
        query = query.where(Violation.site_id == site_id)
    if violation_type:
        query = query.where(Violation.violation_type == ViolationType(violation_type))
    if severity:
        query = query.where(Violation.severity == ViolationSeverity(severity))

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    result = await db.execute(
        query.order_by(Violation.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    violations = result.scalars().all()

    return PaginatedResponse(
        items=[ViolationResponse.model_validate(v) for v in violations],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{violation_id}", response_model=ViolationResponse)
async def get_violation(
    violation_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ViolationResponse:
    result = await db.execute(select(Violation).where(Violation.id == violation_id))
    violation = result.scalar_one_or_none()
    if not violation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Violation not found")
    return ViolationResponse.model_validate(violation)


@router.post("", response_model=ViolationResponse, status_code=status.HTTP_201_CREATED)
async def create_violation(
    data: ViolationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ViolationResponse:
    """Internal endpoint — called by AI engine to log violations."""
    violation = Violation(
        camera_id=data.camera_id,
        site_id=data.site_id,
        violation_type=ViolationType(data.violation_type),
        severity=ViolationSeverity(data.severity),
        confidence=data.confidence,
        tracking_id=data.tracking_id,
        bounding_boxes=[b.model_dump() for b in data.bounding_boxes],
        screenshot_key=data.screenshot_key,
        frame_timestamp=data.frame_timestamp,
        metadata_=data.metadata,
    )
    db.add(violation)
    await db.flush()
    await db.refresh(violation)
    return ViolationResponse.model_validate(violation)


@router.patch("/{violation_id}/acknowledge", response_model=ViolationResponse)
async def acknowledge_violation(
    violation_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.OPERATOR))],
) -> ViolationResponse:
    result = await db.execute(select(Violation).where(Violation.id == violation_id))
    violation = result.scalar_one_or_none()
    if not violation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Violation not found")

    violation.is_acknowledged = True
    violation.acknowledged_by = current_user.id
    violation.acknowledged_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(violation)
    return ViolationResponse.model_validate(violation)
