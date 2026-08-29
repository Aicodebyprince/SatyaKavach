"""
SatyaKavach - Application Configuration
All settings loaded from environment variables with sensible defaults.
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "SatyaKavach"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-Powered Deepfake & Manipulated Media Detection"
    DEBUG: bool = False
    DEMO_MODE: bool = True  # Use mock AI responses for demo

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/satya"

    # S3 / MinIO Storage
    S3_ENDPOINT: str = "http://minio:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "satya-kavach-evidence"
    S3_REGION: str = "us-east-1"

    # JWT Authentication
    JWT_SECRET_KEY: str = "satyakavach-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Gemini API
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_VISION_MODEL: str = "gemini-2.0-flash"

    # Threat Intelligence
    VIRUSTOTAL_API_KEY: str = ""
    GOOGLE_SAFE_BROWSING_API_KEY: str = ""
    PHISHTANK_APP_KEY: str = ""

    # Redis (for Celery)
    REDIS_URL: str = "redis://redis:6379/0"

    # Upload Limits
    MAX_FILE_SIZE_MB: int = 100
    ALLOWED_IMAGE_TYPES: list[str] = ["image/png", "image/jpeg", "image/webp"]
    ALLOWED_VIDEO_TYPES: list[str] = ["video/mp4", "video/quicktime", "video/x-msvideo"]
    ALLOWED_AUDIO_TYPES: list[str] = ["audio/mpeg", "audio/wav", "audio/x-m4a", "audio/mp4"]

    # Risk Engine Weights
    RISK_WEIGHT_IMAGE: float = 0.30
    RISK_WEIGHT_VIDEO: float = 0.25
    RISK_WEIGHT_AUDIO: float = 0.20
    RISK_WEIGHT_OCR_NLP: float = 0.15
    RISK_WEIGHT_THREAT: float = 0.10

    # Trust Score Thresholds
    TRUST_HIGH_THRESHOLD: int = 80
    TRUST_UNCERTAIN_THRESHOLD: int = 50

    # Evidence Retention
    EVIDENCE_RETENTION_DAYS: int = 90

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10

    # CORS — comma-separated in env, defaults include local dev
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:4173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
