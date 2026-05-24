"""Violation rule engine — Blueprint v2.0 (8-class model + temporal 5/15 filter)."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import UUID

import structlog

from app.core.config import get_settings
from app.core.constants import (
    CRITICAL_VIOLATION_CLASSES,
    DIRECT_VIOLATION_CLASSES,
    HIGH_VIOLATION_CLASSES,
    LIFELINE_ENABLED,
)
from app.services.inference import Detection
from app.services.temporal_filter import TemporalViolationFilter

logger = structlog.get_logger(__name__)
settings = get_settings()


class ViolationType(str, Enum):
    HELMET_OFF = "helmet_off"
    HARNESS_OFF = "harness_off"
    RESTRICTED_ZONE = "restricted_zone"
    UNSAFE_CLIMBING = "unsafe_climbing"
    LIFELINE_OFF = "lifeline_off"  # Phase 3+ when lifeline model validated


class ViolationSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"


@dataclass
class ViolationEvent:
    violation_type: ViolationType
    severity: ViolationSeverity
    confidence: float
    tracking_id: Optional[str]
    bounding_boxes: list[dict[str, Any]]
    camera_id: UUID
    frame_timestamp: datetime


class ViolationRuleEngine:
    """
    Evaluates detections using:
    1. Direct violation classes from YOLO (helmet_off, harness_off, unsafe_climbing, restricted_zone)
    2. Derived PPE rules on person_tower (helmet_on/off association)
    3. Polygon restricted zones from camera config
    4. Temporal filter: 5 of 15 frames before alert
    """

    def __init__(self) -> None:
        self._temporal = TemporalViolationFilter(
            threshold=settings.temporal_filter_threshold,
            window=settings.temporal_filter_window,
        )

    def evaluate(
        self,
        camera_id: UUID,
        detections: list[Detection],
        restricted_zones: list[list[float]] | None = None,
    ) -> list[ViolationEvent]:
        violations: list[ViolationEvent] = []
        seen: set[str] = set()

        # Direct model-predicted violations
        for det in detections:
            if det.class_name not in DIRECT_VIOLATION_CLASSES:
                continue
            if det.class_name == "lifeline_attached":
                continue

            track_id = det.tracking_id or f"anon_{id(det)}"
            vtype = ViolationType(det.class_name)
            severity = self._severity_for(vtype)

            if self._temporal.update(track_id, det.class_name, True):
                key = f"{track_id}:{det.class_name}"
                if key not in seen:
                    seen.add(key)
                    violations.append(
                        self._create_violation(vtype, severity, det, detections, camera_id)
                    )

        # Derived rules on person_tower workers
        workers = [d for d in detections if d.class_name == "person_tower"]
        helmets = [d for d in detections if d.class_name in ("helmet_on", "helmet_off")]
        harnesses = [d for d in detections if d.class_name in ("harness_on", "harness_off")]

        for worker in workers:
            track_id = worker.tracking_id or f"worker_{id(worker)}"

            # Helmet: missing or explicit no_helmet overlap
            has_helmet = self._person_has_ppe(worker, helmets, "helmet_on")
            no_helmet = self._person_has_ppe(worker, helmets, "helmet_off")
            if no_helmet or not has_helmet:
                if self._temporal.update(track_id, "helmet_off", True):
                    key = f"{track_id}:helmet_off"
                    if key not in seen:
                        seen.add(key)
                        violations.append(
                            self._create_violation(
                                ViolationType.HELMET_OFF,
                                ViolationSeverity.CRITICAL,
                                worker,
                                detections,
                                camera_id,
                            )
                        )
            else:
                self._temporal.update(track_id, "helmet_off", False)

            # Harness
            has_harness = self._person_has_ppe(worker, harnesses, "harness_on")
            no_harness = self._person_has_ppe(worker, harnesses, "harness_off")
            if no_harness or not has_harness:
                if self._temporal.update(track_id, "harness_off", True):
                    key = f"{track_id}:harness_off"
                    if key not in seen:
                        seen.add(key)
                        violations.append(
                            self._create_violation(
                                ViolationType.HARNESS_OFF,
                                ViolationSeverity.CRITICAL,
                                worker,
                                detections,
                                camera_id,
                            )
                        )
            else:
                self._temporal.update(track_id, "harness_off", False)

            # Config-based restricted zone (polygon from camera settings)
            if restricted_zones and self._in_restricted_zone(worker, restricted_zones):
                if self._temporal.update(track_id, "restricted_zone", True):
                    key = f"{track_id}:restricted_zone"
                    if key not in seen:
                        seen.add(key)
                        violations.append(
                            self._create_violation(
                                ViolationType.RESTRICTED_ZONE,
                                ViolationSeverity.HIGH,
                                worker,
                                detections,
                                camera_id,
                            )
                        )
            else:
                self._temporal.update(track_id, "restricted_zone", False)

        # Lifeline — Phase 3+ only
        if LIFELINE_ENABLED:
            for worker in workers:
                track_id = worker.tracking_id or f"worker_{id(worker)}"
                has_lifeline = any(
                    d.class_name == "lifeline_attached" and self._boxes_overlap(worker, d)
                    for d in detections
                )
                if not has_lifeline and self._temporal.update(track_id, "lifeline_off", True):
                    violations.append(
                        self._create_violation(
                            ViolationType.LIFELINE_OFF,
                            ViolationSeverity.MEDIUM,
                            worker,
                            detections,
                            camera_id,
                        )
                    )

        return violations

    @staticmethod
    def _severity_for(vtype: ViolationType) -> ViolationSeverity:
        if vtype.value in CRITICAL_VIOLATION_CLASSES:
            return ViolationSeverity.CRITICAL
        if vtype.value in HIGH_VIOLATION_CLASSES or vtype == ViolationType.UNSAFE_CLIMBING:
            return ViolationSeverity.HIGH
        return ViolationSeverity.MEDIUM

    def _person_has_ppe(
        self, person: Detection, ppe_detections: list[Detection], positive_class: str
    ) -> bool:
        return any(
            p.class_name == positive_class and self._boxes_overlap(person, p)
            for p in ppe_detections
        )

    def _in_restricted_zone(self, person: Detection, zones: list[list[float]]) -> bool:
        px, py = person.x, person.y
        for zone in zones:
            if len(zone) < 6:
                continue
            n = len(zone) // 2
            inside = False
            j = n - 1
            for i in range(n):
                xi, yi = zone[i * 2], zone[i * 2 + 1]
                xj, yj = zone[j * 2], zone[j * 2 + 1]
                if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
                    inside = not inside
                j = i
            if inside:
                return True
        return False

    def _create_violation(
        self,
        violation_type: ViolationType,
        severity: ViolationSeverity,
        anchor: Detection,
        all_detections: list[Detection],
        camera_id: UUID,
    ) -> ViolationEvent:
        return ViolationEvent(
            violation_type=violation_type,
            severity=severity,
            confidence=anchor.confidence,
            tracking_id=anchor.tracking_id,
            bounding_boxes=[
                {
                    "class_name": d.class_name,
                    "x": d.x,
                    "y": d.y,
                    "w": d.w,
                    "h": d.h,
                    "confidence": d.confidence,
                    "tracking_id": d.tracking_id,
                }
                for d in all_detections
            ],
            camera_id=camera_id,
            frame_timestamp=datetime.now(timezone.utc),
        )

    @staticmethod
    def _boxes_overlap(a: Detection, b: Detection, threshold: float = 0.3) -> bool:
        ax1, ay1 = a.x - a.w / 2, a.y - a.h / 2
        ax2, ay2 = a.x + a.w / 2, a.y + a.h / 2
        bx1, by1 = b.x - b.w / 2, b.y - b.h / 2
        bx2, by2 = b.x + b.w / 2, b.y + b.h / 2
        ix1, iy1 = max(ax1, bx1), max(ay1, by1)
        ix2, iy2 = min(ax2, bx2), min(ay2, by2)
        inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
        area_a = a.w * a.h
        return (inter / area_a) > threshold if area_a > 0 else False
