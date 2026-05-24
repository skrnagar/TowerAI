"""Detection classes, thresholds, and model mappings — Blueprint v2.0."""

from enum import Enum


class DetectionClass(str, Enum):
    """Eight-class YOLO detection taxonomy (Blueprint v2.0)."""

    HELMET_ON = "helmet_on"
    HELMET_OFF = "helmet_off"
    HARNESS_ON = "harness_on"
    HARNESS_OFF = "harness_off"
    PERSON_TOWER = "person_tower"
    UNSAFE_CLIMBING = "unsafe_climbing"
    RESTRICTED_ZONE = "restricted_zone"
    LIFELINE_ATTACHED = "lifeline_attached"


# YOLO class ID → enum (matches dataset/data.yaml)
CLASS_ID_MAP: dict[int, DetectionClass] = {
    0: DetectionClass.HELMET_ON,
    1: DetectionClass.HELMET_OFF,
    2: DetectionClass.HARNESS_ON,
    3: DetectionClass.HARNESS_OFF,
    4: DetectionClass.PERSON_TOWER,
    5: DetectionClass.UNSAFE_CLIMBING,
    6: DetectionClass.RESTRICTED_ZONE,
    7: DetectionClass.LIFELINE_ATTACHED,
}

CLASS_NAMES: list[str] = [c.value for c in DetectionClass]

# Per-class confidence thresholds — recall-first on critical violations
CLASS_CONFIDENCE_THRESHOLDS: dict[str, float] = {
    DetectionClass.HELMET_OFF.value: 0.35,
    DetectionClass.HARNESS_OFF.value: 0.35,
    DetectionClass.UNSAFE_CLIMBING.value: 0.45,
    DetectionClass.RESTRICTED_ZONE.value: 0.50,
    DetectionClass.PERSON_TOWER.value: 0.40,
    DetectionClass.HELMET_ON.value: 0.55,
    DetectionClass.HARNESS_ON.value: 0.55,
    DetectionClass.LIFELINE_ATTACHED.value: 0.60,
}

# Direct violation classes (model predicts violation explicitly)
DIRECT_VIOLATION_CLASSES: set[str] = {
    DetectionClass.HELMET_OFF.value,
    DetectionClass.HARNESS_OFF.value,
    DetectionClass.UNSAFE_CLIMBING.value,
    DetectionClass.RESTRICTED_ZONE.value,
}

CRITICAL_VIOLATION_CLASSES: set[str] = {
    DetectionClass.HELMET_OFF.value,
    DetectionClass.HARNESS_OFF.value,
}

HIGH_VIOLATION_CLASSES: set[str] = {
    DetectionClass.UNSAFE_CLIMBING.value,
    DetectionClass.RESTRICTED_ZONE.value,
}

# Phase 3+ — lifeline detection enabled when model accuracy validated
LIFELINE_ENABLED: bool = False

# Primary / ensemble model paths (Phase 1: single model; Phase 3: ensemble)
DEFAULT_PRIMARY_MODEL = "yolov8x.pt"
DEFAULT_ENSEMBLE_MODEL = "yolov9e.pt"
