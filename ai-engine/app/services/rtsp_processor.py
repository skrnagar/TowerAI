"""RTSP stream ingestion — multi-camera frame capture."""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Callable, Optional
from uuid import UUID

import cv2
import numpy as np
import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


@dataclass
class CameraStream:
    camera_id: UUID
    rtsp_url: str
    fps: int = 15
    is_running: bool = False
    last_frame: Optional[np.ndarray] = None
    last_frame_time: float = 0.0
    reconnect_count: int = 0
    _cap: Optional[cv2.VideoCapture] = field(default=None, repr=False)


class RTSPProcessor:
    """
    Manages multiple RTSP camera streams.
    Captures frames asynchronously and pushes to frame queue for AI inference.
    """

    def __init__(self) -> None:
        self.streams: dict[UUID, CameraStream] = {}
        self._tasks: dict[UUID, asyncio.Task] = {}
        self._frame_callbacks: list[Callable] = []

    def register_callback(self, callback: Callable) -> None:
        self._frame_callbacks.append(callback)

    async def add_camera(self, camera_id: UUID, rtsp_url: str, fps: int = 15) -> None:
        if camera_id in self.streams:
            await self.remove_camera(camera_id)

        stream = CameraStream(camera_id=camera_id, rtsp_url=rtsp_url, fps=fps)
        self.streams[camera_id] = stream
        self._tasks[camera_id] = asyncio.create_task(self._capture_loop(stream))
        logger.info("camera_added", camera_id=str(camera_id), rtsp_url=rtsp_url)

    async def remove_camera(self, camera_id: UUID) -> None:
        if camera_id in self._tasks:
            self._tasks[camera_id].cancel()
            del self._tasks[camera_id]
        if camera_id in self.streams:
            self.streams[camera_id].is_running = False
            del self.streams[camera_id]
        logger.info("camera_removed", camera_id=str(camera_id))

    async def _capture_loop(self, stream: CameraStream) -> None:
        frame_interval = 1.0 / stream.fps
        stream.is_running = True

        while stream.is_running:
            try:
                if stream._cap is None or not stream._cap.isOpened():
                    stream._cap = cv2.VideoCapture(stream.rtsp_url)
                    stream._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    if not stream._cap.isOpened():
                        raise ConnectionError(f"Failed to open RTSP stream: {stream.rtsp_url}")

                ret, frame = stream._cap.read()
                if not ret:
                    raise ConnectionError("Frame read failed")

                stream.last_frame = frame
                stream.last_frame_time = time.time()
                stream.reconnect_count = 0

                for callback in self._frame_callbacks:
                    await callback(stream.camera_id, frame)

                await asyncio.sleep(frame_interval)

            except (ConnectionError, cv2.error) as e:
                stream.reconnect_count += 1
                logger.warning(
                    "rtsp_reconnect",
                    camera_id=str(stream.camera_id),
                    attempt=stream.reconnect_count,
                    error=str(e),
                )
                if stream._cap:
                    stream._cap.release()
                    stream._cap = None
                await asyncio.sleep(settings.rtsp_reconnect_delay_seconds)

    def get_latest_frame(self, camera_id: UUID) -> Optional[np.ndarray]:
        stream = self.streams.get(camera_id)
        return stream.last_frame if stream else None
