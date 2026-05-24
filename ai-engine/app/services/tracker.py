"""DeepSORT multi-object tracking for worker identity persistence."""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import structlog

from app.services.inference import Detection

logger = structlog.get_logger(__name__)


@dataclass
class TrackedObject:
    tracking_id: str
    class_name: str
    bbox: tuple[float, float, float, float]  # x, y, w, h normalized
    confidence: float
    frames_seen: int = 1
    last_seen_frame: int = 0


class DeepSORTTracker:
    """
    DeepSORT-based multi-object tracker.
    Assigns persistent tracking IDs to detected workers across frames.
    Implementation placeholder — full DeepSORT integration in Step 9.
    """

    def __init__(self, max_age: int = 30, min_hits: int = 3) -> None:
        self.max_age = max_age
        self.min_hits = min_hits
        self._tracks: dict[str, TrackedObject] = {}
        self._next_id = 1
        self._frame_count = 0

    def update(self, detections: list[Detection]) -> list[Detection]:
        self._frame_count += 1
        tracked: list[Detection] = []

        for det in detections:
            if det.class_name not in ("person", "person_tower"):
                tracked.append(det)
                continue

            # Simple IOU-based association placeholder — replaced with DeepSORT in Step 9
            track_id = self._assign_track(det)
            det.tracking_id = track_id
            tracked.append(det)

        self._cleanup_stale_tracks()
        return tracked

    def _assign_track(self, detection: Detection) -> str:
        best_match: Optional[str] = None
        best_iou = 0.3

        for track_id, track in self._tracks.items():
            if track.class_name not in ("person", "person_tower"):
                continue
            iou = self._compute_iou(
                (detection.x, detection.y, detection.w, detection.h),
                track.bbox,
            )
            if iou > best_iou:
                best_iou = iou
                best_match = track_id

        if best_match:
            track = self._tracks[best_match]
            track.bbox = (detection.x, detection.y, detection.w, detection.h)
            track.confidence = detection.confidence
            track.frames_seen += 1
            track.last_seen_frame = self._frame_count
            return best_match

        new_id = f"worker_{self._next_id}"
        self._next_id += 1
        self._tracks[new_id] = TrackedObject(
            tracking_id=new_id,
            class_name=detection.class_name,
            bbox=(detection.x, detection.y, detection.w, detection.h),
            confidence=detection.confidence,
            last_seen_frame=self._frame_count,
        )
        return new_id

    def _cleanup_stale_tracks(self) -> None:
        stale = [
            tid
            for tid, track in self._tracks.items()
            if self._frame_count - track.last_seen_frame > self.max_age
        ]
        for tid in stale:
            del self._tracks[tid]

    @staticmethod
    def _compute_iou(box1: tuple, box2: tuple) -> float:
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2

        xi1 = max(x1 - w1 / 2, x2 - w2 / 2)
        yi1 = max(y1 - h1 / 2, y2 - h2 / 2)
        xi2 = min(x1 + w1 / 2, x2 + w2 / 2)
        yi2 = min(y1 + h1 / 2, y2 + h2 / 2)

        inter = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        union = w1 * h1 + w2 * h2 - inter
        return inter / union if union > 0 else 0.0
