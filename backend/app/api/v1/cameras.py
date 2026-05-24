"""Camera management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.core.security import UserRole
from app.db.models import Camera, User
from app.db.session import get_db
from app.schemas import CameraCreate, CameraResponse, CameraUpdate, PaginatedResponse

router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.get("", response_model=PaginatedResponse)
async def list_cameras(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    site_id: UUID | None = None,
) -> PaginatedResponse:
    query = select(Camera).where(Camera.is_active == True)  # noqa: E712
    if site_id:
        query = query.where(Camera.site_id == site_id)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    result = await db.execute(
        query.order_by(Camera.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    cameras = result.scalars().all()

    return PaginatedResponse(
        items=[CameraResponse.model_validate(c) for c in cameras],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CameraResponse:
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return CameraResponse.model_validate(camera)


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(
    data: CameraCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.SUPERVISOR))],
) -> CameraResponse:
    camera = Camera(**data.model_dump())
    db.add(camera)
    await db.flush()
    await db.refresh(camera)
    return CameraResponse.model_validate(camera)


@router.patch("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: UUID,
    data: CameraUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.SUPERVISOR))],
) -> CameraResponse:
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(camera, field, value)

    await db.flush()
    await db.refresh(camera)
    return CameraResponse.model_validate(camera)
