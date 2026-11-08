from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Security
    API_KEY: str = "dev-key-change-in-production"
    JWT_SECRET_KEY: str = "change-this-jwt-secret-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://peopledoxx:peopledoxx@localhost:5432/peopledoxx"
    )

    # Cache
    CACHE_TTL_SECONDS: int = 3600

    # Scraper behaviour (global default — overridden per-user via quota)
    REQUEST_DELAY_SECONDS: float = 1.0

    # Logging
    LOG_LEVEL: str = "INFO"

    # Environment
    ENVIRONMENT: str = "development"

    # Admin bootstrap (first run)
    ADMIN_EMAIL: str = "admin@peopledoxx.local"
    ADMIN_PASSWORD: str = "ChangeMe!2024"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached Settings singleton."""
    return Settings()
