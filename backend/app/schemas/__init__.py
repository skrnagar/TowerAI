"""Pydantic request/response schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    email: str  # allows dev seed admin@towerai.local (EmailStr rejects .local TLD)
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    role: str
    site_id: Optional[UUID] = None
    is_active: bool


# ---------------------------------------------------------------------------
# Cameras
# ---------------------------------------------------------------------------
class CameraCreate(BaseModel):
    site_id: UUID
    name: str
    code: str
    rtsp_url: str
    location_label: Optional[str] = None
    fps: int = 15
    resolution: str = "1920x1080"
    restricted_zones: list[list[float]] = Field(default_factory=list)


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    location_label: Optional[str] = None
    fps: Optional[int] = None
    restricted_zones: Optional[list[list[float]]] = None
    is_active: Optional[bool] = None


class CameraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    site_id: UUID
    name: str
    code: str
    rtsp_url: str
    location_label: Optional[str] = None
    status: str
    fps: int
    resolution: str
    restricted_zones: list[Any]
    is_active: bool
    last_seen_at: Optional[datetime] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Violations
# ---------------------------------------------------------------------------
class BoundingBox(BaseModel):
    class_name: str
    x: float
    y: float
    w: float
    h: float
    confidence: float
    tracking_id: Optional[str] = None


class ViolationCreate(BaseModel):
    camera_id: UUID
    site_id: UUID
    violation_type: str
    severity: str
    confidence: float
    tracking_id: Optional[str] = None
    bounding_boxes: list[BoundingBox]
    screenshot_key: Optional[str] = None
    frame_timestamp: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class ViolationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    camera_id: UUID
    site_id: UUID
    violation_type: str
    severity: str
    confidence: float
    tracking_id: Optional[str] = None
    bounding_boxes: list[Any]
    screenshot_url: Optional[str] = None
    frame_timestamp: datetime
    is_acknowledged: bool
    created_at: datetime


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------
class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    violation_id: UUID
    camera_id: UUID
    site_id: UUID
    title: str
    message: str
    severity: str
    status: str
    created_at: datetime
    updated_at: datetime


class AlertUpdate(BaseModel):
    status: Optional[str] = None
    resolution_note: Optional[str] = None


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
class DashboardStats(BaseModel):
    total_cameras: int
    online_cameras: int
    total_violations_today: int
    critical_violations_today: int
    pending_alerts: int
    violations_by_type: dict[str, int]
    recent_violations: list[ViolationResponse]


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
