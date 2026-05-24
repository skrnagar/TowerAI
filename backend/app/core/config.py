"""Application configuration via environment variables."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # General
    environment: str = "development"
    debug: bool = True
    secret_key: str = "change-me"
    api_v1_prefix: str = "/api/v1"

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://towerai:towerai_secure_password@localhost:5432/towerai_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # JWT
    jwt_secret_key: str = "change-me-jwt"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # CORS
    cors_origins: str = "http://localhost:3000"

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "towerai_minio"
    minio_secret_key: str = "towerai_minio_secret"
    minio_bucket_violations: str = "towerai-violations"
    minio_bucket_recordings: str = "towerai-recordings"
    minio_use_ssl: bool = False

    # AI Engine
    ai_engine_url: str = "http://localhost:8001"

    # WebSocket
    ws_heartbeat_interval: int = 30
    ws_max_connections: int = 100

    # Logging
    log_level: str = "INFO"

    # Notifications (Blueprint v2.0)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = ""
    alert_supervisor_phone: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
