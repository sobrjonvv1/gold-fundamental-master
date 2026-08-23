import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import field_validator

    class Settings(BaseSettings):
        PROJECT_NAME: str = "GOLD FUNDAMENTAL MASTER"
        APP_ENV: str = "development"
        DEBUG: bool = False
        SECRET_KEY: str = ""

        DATABASE_URL: str = "sqlite+aiosqlite:///./gold_fundamental.db"
        REDIS_URL: str = "redis://localhost:6379/0"
        REDIS_SOCKET_TIMEOUT_SECONDS: float = 1.0

        TELEGRAM_BOT_TOKEN: str = ""
        TELEGRAM_WEBAPP_URL: Optional[str] = None
        TELEGRAM_POLLING_ENABLED: bool = False
        TELEGRAM_RESTART_MAX_DELAY_SECONDS: int = 60
        BACKEND_URL: Optional[str] = None

        OPENROUTER_API_KEY: str = ""
        OPENROUTER_MODEL: str = "openrouter/free"
        OPENROUTER_FALLBACK_MODEL: str = "meta-llama/llama-3.2-3b-instruct:free"
        LLM_DAILY_REQUEST_LIMIT: int = 45

        FOREX_FACTORY_PROVIDER: str = "live"
        FOREX_FACTORY_API_KEY: str = ""
        FED_PROVIDER: str = "mock"
        FED_API_KEY: str = ""
        MARKET_DATA_PROVIDER: str = "mock"
        MARKET_DATA_API_KEY: str = ""
        NEWS_PROVIDER: str = "mock"
        NEWS_API_KEY: str = ""

        SESSION_ASIA_OPEN: str = "05:00"
        SESSION_LONDON_OPEN: str = "13:00"
        SESSION_NEW_YORK_OPEN: str = "18:00"
        DEFAULT_TIMEZONE: str = "Asia/Tashkent"
        CORS_ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
        RATE_LIMIT_PER_MINUTE: int = 120
        TRUST_PROXY_HEADERS: bool = False
        SCHEDULER_ENABLED: bool = True

        MOCK_MODE: bool = True

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore"
        )

        @field_validator(
            "SESSION_ASIA_OPEN", "SESSION_LONDON_OPEN", "SESSION_NEW_YORK_OPEN"
        )
        @classmethod
        def validate_session_time(cls, value: str) -> str:
            try:
                hour, minute = map(int, value.split(":"))
            except ValueError as exc:
                raise ValueError("must use HH:MM format") from exc
            if not 0 <= hour <= 23 or not 0 <= minute <= 59:
                raise ValueError("must be a valid UTC time")
            return f"{hour:02d}:{minute:02d}"

        @property
        def cors_origins(self) -> list[str]:
            return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

    settings = Settings()

except ImportError:
    # Standalone Fallback for running tests on bare Python without installed packages
    class SettingsFallback:
        PROJECT_NAME = "GOLD FUNDAMENTAL MASTER"
        APP_ENV = os.getenv("APP_ENV", "development")
        DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        SECRET_KEY = os.getenv("SECRET_KEY", "")
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./gold_fundamental.db")
        REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        REDIS_SOCKET_TIMEOUT_SECONDS = float(os.getenv("REDIS_SOCKET_TIMEOUT_SECONDS", "1.0"))
        TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
        TELEGRAM_WEBAPP_URL = os.getenv("TELEGRAM_WEBAPP_URL")
        TELEGRAM_POLLING_ENABLED = os.getenv("TELEGRAM_POLLING_ENABLED", "false").lower() == "true"
        TELEGRAM_RESTART_MAX_DELAY_SECONDS = int(os.getenv("TELEGRAM_RESTART_MAX_DELAY_SECONDS", "60"))
        BACKEND_URL = os.getenv("BACKEND_URL")
        OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
        OPENROUTER_MODEL = "google/gemini-2.0-flash-001"
        OPENROUTER_FALLBACK_MODEL = "meta-llama/llama-3.3-70b-instruct"
        LLM_DAILY_REQUEST_LIMIT = 100
        FOREX_FACTORY_PROVIDER = "mock"
        FOREX_FACTORY_API_KEY = ""
        FED_PROVIDER = "mock"
        FED_API_KEY = ""
        MARKET_DATA_PROVIDER = "mock"
        MARKET_DATA_API_KEY = ""
        NEWS_PROVIDER = "mock"
        NEWS_API_KEY = ""
        SESSION_ASIA_OPEN = os.getenv("SESSION_ASIA_OPEN", "00:00")
        SESSION_LONDON_OPEN = os.getenv("SESSION_LONDON_OPEN", "08:00")
        SESSION_NEW_YORK_OPEN = os.getenv("SESSION_NEW_YORK_OPEN", "13:00")
        DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "UTC")
        CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
        RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
        TRUST_PROXY_HEADERS = os.getenv("TRUST_PROXY_HEADERS", "false").lower() == "true"
        SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"
        MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"

        @property
        def cors_origins(self) -> list[str]:
            return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

    settings = SettingsFallback()


def validate_production_settings() -> None:
    """Fail early for unsafe production configuration, never for local tests."""
    if settings.APP_ENV.lower() != "production":
        return
    if not settings.SECRET_KEY or settings.SECRET_KEY.startswith("change_this"):
        raise RuntimeError("SECRET_KEY must be set to a random production secret")
    if not settings.cors_origins or "*" in settings.cors_origins:
        raise RuntimeError("CORS_ALLOWED_ORIGINS must contain explicit HTTPS origins in production")
    if any(not origin.startswith("https://") for origin in settings.cors_origins):
        raise RuntimeError("CORS_ALLOWED_ORIGINS must use HTTPS origins in production")
    if settings.DATABASE_URL.startswith("sqlite"):
        raise RuntimeError("DATABASE_URL must point to production PostgreSQL")
    if settings.TELEGRAM_POLLING_ENABLED and not settings.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required when polling is enabled")
    if settings.TELEGRAM_POLLING_ENABLED and (
        not settings.TELEGRAM_WEBAPP_URL or not settings.TELEGRAM_WEBAPP_URL.startswith("https://")
    ):
        raise RuntimeError("TELEGRAM_WEBAPP_URL must be an HTTPS URL when polling is enabled")
