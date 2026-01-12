from functools import lru_cache
from typing import Any, Dict, Optional

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 86400  # 24 hours

    # Security & Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Rate Limiting
    RATE_LIMIT_AUTH: str = "5/minute"
    RATE_LIMIT_GENERAL: str = "60/minute"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:19006"
    CORS_ALLOW_CREDENTIALS: bool = True

    # External APIs - Google Books
    GOOGLE_BOOKS_API_KEY: Optional[str] = None
    GOOGLE_BOOKS_BASE_URL: str = "https://www.googleapis.com/books/v1"

    # External APIs - Hugging Face (IA para classificação e geração)
    HUGGINGFACE_API_KEY: Optional[str] = None
    HUGGINGFACE_BASE_URL: str = "https://router.huggingface.co/models"
    MODEL_NAME: str = "ProsusAI/finbert"  # Classificação de gêneros
    TEXT_GENERATION_MODEL: str = "meta-llama/Llama-3.1-8B-Instruct"  # Geração de jogos
    AI_REQUEST_TIMEOUT: int = 30
    AI_RETRY_MAX_ATTEMPTS: int = 3
    AI_RETRY_BACKOFF_FACTOR: int = 2

    # Email (Future)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@book2game.com"

    # Logging
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "7 days"
    LOG_FORMAT: str = "json"

    # Deployment
    RAILWAY_ENVIRONMENT: Optional[str] = None
    RENDER_EXTERNAL_URL: Optional[str] = None

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string to list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure secret key is strong enough."""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
