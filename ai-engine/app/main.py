"""AI Engine main entry point — orchestrates RTSP, inference, tracking, and violations."""

import asyncio

import structlog
import uvicorn
from fastapi import FastAPI

from app import __version__
from app.core.config import get_settings
from app.services.inference import YOLOInferenceEngine
from app.services.rtsp_processor import RTSPProcessor
from app.services.tracker import DeepSORTTracker
from app.services.violation_engine import ViolationRuleEngine

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
)
logger = structlog.get_logger(__name__)
settings = get_settings()

# Global service instances
rtsp_processor = RTSPProcessor()
inference_engine = YOLOInferenceEngine()
tracker = DeepSORTTracker()
violation_engine = ViolationRuleEngine()

app = FastAPI(
    title="Tower AI — Inference Engine",
    version=__version__,
    docs_url="/docs",
)


@app.on_event("startup")
async def startup() -> None:
    logger.info("ai_engine_starting", version=__version__)
    inference_engine.initialize()
    rtsp_processor.register_callback(process_frame)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "healthy",
        "version": __version__,
        "active_cameras": len(rtsp_processor.streams),
        "device": inference_engine.device,
    }


async def process_frame(camera_id, frame) -> None:
    """Pipeline: inference → tracking → violation check → alert."""
    detections = inference_engine.infer(frame)
    tracked = tracker.update(detections)
    violations = violation_engine.evaluate(camera_id, tracked)
    if violations:
        logger.warning(
            "violations_detected",
            camera_id=str(camera_id),
            count=len(violations),
            types=[v.violation_type.value for v in violations],
        )
        # Step 13: push to backend via HTTP + Redis pub/sub


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host=settings.ai_engine_host,
        port=settings.ai_engine_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
