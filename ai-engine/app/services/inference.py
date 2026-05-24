"""YOLOv8/v9 inference with per-class thresholds and optional ensemble — Blueprint v2.0."""

import time
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np
import structlog

from app.core.config import get_settings
from app.core.constants import CLASS_CONFIDENCE_THRESHOLDS, CLASS_ID_MAP

logger = structlog.get_logger(__name__)
settings = get_settings()


@dataclass
class Detection:
    class_name: str
    confidence: float
    x: float
    y: float
    w: float
    h: float
    tracking_id: Optional[str] = None


class YOLOInferenceEngine:
    """
    Primary YOLOv8x inference engine.
    Phase 3: enable ensemble via ai_ensemble_enabled + secondary model.
    Target: 5 FPS per camera at 640×640.
    """

    def __init__(self) -> None:
        self.model: Any = None
        self.model_ensemble: Any = None
        self.device = "cpu"
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return

        try:
            import torch
            from ultralytics import YOLO

            self.device = "cuda" if settings.ai_gpu_enabled and torch.cuda.is_available() else "cpu"
            self.model = YOLO(settings.yolo_model_path)

            if settings.ai_ensemble_enabled:
                self.model_ensemble = YOLO(settings.yolo_ensemble_model_path)
                logger.info("ensemble_model_loaded", path=settings.yolo_ensemble_model_path)

            self._initialized = True
            logger.info("yolo_initialized", device=self.device, model=settings.yolo_model_path)
        except Exception as e:
            logger.error("yolo_init_failed", error=str(e))
            raise

    def infer(self, frame: np.ndarray) -> list[Detection]:
        if not self._initialized:
            self.initialize()

        start = time.perf_counter()

        if settings.ai_ensemble_enabled and self.model_ensemble is not None:
            detections = self._infer_ensemble(frame)
        else:
            detections = self._parse_results(
                self.model(
                    frame,
                    verbose=False,
                    device=self.device,
                    imgsz=settings.ai_inference_imgsz,
                )
            )

        inference_ms = (time.perf_counter() - start) * 1000
        logger.debug("inference_complete", detections=len(detections), ms=round(inference_ms, 1))
        return detections

    def _infer_ensemble(self, frame: np.ndarray) -> list[Detection]:
        from app.services.ensemble import ensemble_predict

        boxes, scores, labels = ensemble_predict(
            frame,
            self.model,
            self.model_ensemble,
            imgsz=settings.ai_inference_imgsz,
        )
        h, w = frame.shape[:2]
        detections: list[Detection] = []
        for box, score, label in zip(boxes, scores, labels):
            cls_id = int(label)
            detection_class = CLASS_ID_MAP.get(cls_id)
            if detection_class is None:
                continue
            class_name = detection_class.value
            threshold = CLASS_CONFIDENCE_THRESHOLDS.get(class_name, 0.5)
            if float(score) < threshold:
                continue
            x1, y1, x2, y2 = box
            detections.append(
                Detection(
                    class_name=class_name,
                    confidence=float(score),
                    x=(x1 + x2) / 2,
                    y=(y1 + y2) / 2,
                    w=x2 - x1,
                    h=y2 - y1,
                )
            )
        return detections

    def _parse_results(self, results: Any) -> list[Detection]:
        detections: list[Detection] = []
        for result in results:
            if result.boxes is None:
                continue
            h, w = result.orig_shape
            for box in result.boxes:
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                detection_class = CLASS_ID_MAP.get(cls_id)
                if detection_class is None:
                    continue

                class_name = detection_class.value
                threshold = CLASS_CONFIDENCE_THRESHOLDS.get(class_name, 0.5)
                if confidence < threshold:
                    continue

                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append(
                    Detection(
                        class_name=class_name,
                        confidence=confidence,
                        x=((x1 + x2) / 2) / w,
                        y=((y1 + y2) / 2) / h,
                        w=(x2 - x1) / w,
                        h=(y2 - y1) / h,
                    )
                )
        return detections

    def infer_batch(self, frames: list[np.ndarray]) -> list[list[Detection]]:
        if not self._initialized:
            self.initialize()
        return [self.infer(frame) for frame in frames]
