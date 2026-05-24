"""Ensemble inference via Weighted Box Fusion — Blueprint v2.0 Phase 3."""

from typing import Any

import numpy as np
import structlog

logger = structlog.get_logger(__name__)

# Optional dependency — install ensemble-boxes in Phase 3
try:
    from ensemble_boxes import weighted_boxes_fusion

    WBF_AVAILABLE = True
except ImportError:
    WBF_AVAILABLE = False


def ensemble_predict(
    frame: np.ndarray,
    model_primary: Any,
    model_secondary: Any,
    weights: tuple[float, float] = (1.5, 1.0),
    iou_thr: float = 0.55,
    conf_thr: float = 0.25,
    imgsz: int = 640,
) -> tuple[list, list, list]:
    """
    Run YOLOv8x + YOLOv9e and fuse boxes with Weighted Box Fusion.
    Adds ~2–4% mAP over single-model inference.
    """
    if not WBF_AVAILABLE:
        raise RuntimeError("ensemble-boxes not installed. pip install ensemble-boxes")

    r1 = model_primary(frame, conf=conf_thr, imgsz=imgsz, verbose=False)[0]
    r2 = model_secondary(frame, conf=conf_thr, imgsz=imgsz, verbose=False)[0]

    boxes_list = [
        r1.boxes.xyxyn.tolist() if r1.boxes is not None else [],
        r2.boxes.xyxyn.tolist() if r2.boxes is not None else [],
    ]
    scores_list = [
        r1.boxes.conf.tolist() if r1.boxes is not None else [],
        r2.boxes.conf.tolist() if r2.boxes is not None else [],
    ]
    labels_list = [
        r1.boxes.cls.tolist() if r1.boxes is not None else [],
        r2.boxes.cls.tolist() if r2.boxes is not None else [],
    ]

    boxes, scores, labels = weighted_boxes_fusion(
        boxes_list,
        scores_list,
        labels_list,
        weights=list(weights),
        iou_thr=iou_thr,
        skip_box_thr=conf_thr,
    )
    return boxes, scores, labels
