"""AI Engine configuration — aligned with Technical Blueprint v2.0."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Server
    ai_engine_host: str = "0.0.0.0"
    ai_engine_port: int = 8001

    # Models — YOLOv8x primary (Blueprint v2.0); YOLOv9e for ensemble Phase 3
    yolo_model_path: str = "/models/tower_safety/best.pt"
    yolo_ensemble_model_path: str = "/models/tower_safety/yolov9e_best.pt"
    yolo_pose_model_path: str = "/models/yolov8n-pose.pt"
    ai_ensemble_enabled: bool = False
    ai_pose_enabled: bool = False
    ai_gpu_enabled: bool = True
    ai_batch_size: int = 4
    ai_inference_imgsz: int = 640

    # VLM secondary verifier (Phase 4) — invoked when confidence < threshold
    vlm_verifier_enabled: bool = False
    vlm_confidence_trigger: float = 0.70
    vlm_provider: str = "openai"  # openai | anthropic
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Processing rates
    ai_inference_fps: int = 5
    ai_stream_fps: int = 15
    ai_frame_skip_ratio: int = 6  # infer every Nth frame at 30 FPS source → ~5 FPS

    # Temporal filter — 5 violations in 15-frame window (Blueprint v2.0)
    temporal_filter_threshold: int = 5
    temporal_filter_window: int = 15

    # Legacy alias
    temporal_filter_frames: int = 5

    # RTSP
    rtsp_frame_buffer_size: int = 1  # low latency
    rtsp_reconnect_delay_seconds: int = 5

    # External services
    redis_url: str = "redis://localhost:6379/0"
    backend_url: str = "http://localhost:8000"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "towerai_minio"
    minio_secret_key: str = "towerai_minio_secret"
    minio_bucket_violations: str = "towerai-violations"

    # Notifications (Phase 2+)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = ""
    alert_supervisor_phone: str = ""


@lru_cache
def get_settings() -> AISettings:
    return AISettings()
