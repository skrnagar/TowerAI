"""Real-time WebSocket gateway for live feed, alerts, and detection overlays."""

import asyncio
import json
from typing import Any
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections with channel-based pub/sub."""

    def __init__(self) -> None:
        self.active_connections: dict[str, list[WebSocket]] = {
            "dashboard": [],
            "alerts": [],
            "cameras": [],
        }
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, channel: str = "dashboard") -> None:
        await websocket.accept()
        async with self._lock:
            if channel not in self.active_connections:
                self.active_connections[channel] = []
            self.active_connections[channel].append(websocket)
        logger.info("websocket_connected", channel=channel, total=len(self.active_connections[channel]))

    async def disconnect(self, websocket: WebSocket, channel: str = "dashboard") -> None:
        async with self._lock:
            if channel in self.active_connections:
                self.active_connections[channel] = [
                    ws for ws in self.active_connections[channel] if ws != websocket
                ]
        logger.info("websocket_disconnected", channel=channel)

    async def broadcast(self, channel: str, message: dict[str, Any]) -> None:
        async with self._lock:
            connections = list(self.active_connections.get(channel, []))

        dead: list[WebSocket] = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)

        if dead:
            async with self._lock:
                self.active_connections[channel] = [
                    ws for ws in self.active_connections.get(channel, []) if ws not in dead
                ]

    async def send_to_camera_subscribers(self, camera_id: UUID, message: dict[str, Any]) -> None:
        """Send detection overlay updates to clients subscribed to a specific camera."""
        message["camera_id"] = str(camera_id)
        await self.broadcast("cameras", message)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_dashboard(websocket: WebSocket) -> None:
    """Main dashboard WebSocket — receives alerts, stats, and system events."""
    await manager.connect(websocket, "dashboard")
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        await manager.disconnect(websocket, "dashboard")


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket) -> None:
    """Dedicated alert stream for real-time safety notifications."""
    await manager.connect(websocket, "alerts")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket, "alerts")


@router.websocket("/ws/cameras/{camera_id}")
async def websocket_camera_feed(websocket: WebSocket, camera_id: UUID) -> None:
    """Per-camera WebSocket for live detection overlays and frame metadata."""
    await manager.connect(websocket, "cameras")
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "ping":
                await websocket.send_json({"type": "pong", "camera_id": str(camera_id)})
    except WebSocketDisconnect:
        await manager.disconnect(websocket, "cameras")
