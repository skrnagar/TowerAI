"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1 import alerts, auth, cameras, dashboard, violations

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(cameras.router)
api_router.include_router(violations.router)
api_router.include_router(alerts.router)
api_router.include_router(dashboard.router)
