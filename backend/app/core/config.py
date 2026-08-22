import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        PROJECT_NAME: str = "GOLD FUNDAMENTAL MASTER"
        APP_ENV: str = "production"
        DEBUG: bool = False
        SECRET_KEY: str = "default_secret_key_change_in_production"

        DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/gold_fundamental"
        REDIS_URL: str = "redis://localhost:6379/0"

        TELEGRAM_BOT_TOKEN: str = ""
        TELEGRAM_WEBHOOK_URL: Optional[str] = None
        TELEGRAM_WEBAPP_URL: Optional[str] = None

        OPENROUTER_API_KEY: str = ""
        OPENROUTER_MODEL: str = "google/gemini-2.0-flash-001"
        OPENROUTER_FALLBACK_MODEL: str = "meta-llama/llama-3.3-70b-instruct"
        LLM_DAILY_REQUEST_LIMIT: int = 100

        FOREX_FACTORY_PROVIDER: str = "mock"
        FOREX_FACTORY_API_KEY: str = ""
        FED_PROVIDER: str = "mock"
        FED_API_KEY: str = ""
        MARKET_DATA_PROVIDER: str = "mock"
        MARKET_DATA_API_KEY: str = ""
        NEWS_PROVIDER: str = "mock"
        NEWS_API_KEY: str = ""

        SESSION_ASIA_OPEN: str = "00:00"
        SESSION_LONDON_OPEN: str = "08:00"
        SESSION_NEW_YORK_OPEN: str = "13:00"
        DEFAULT_TIMEZONE: str = "UTC"

        MOCK_MODE: bool = True

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore"
        )

    settings = Settings()

except ImportError:
    # Standalone Fallback for running tests on bare Python without installed packages
    class SettingsFallback:
        PROJECT_NAME = "GOLD FUNDAMENTAL MASTER"
        APP_ENV = "production"
        DEBUG = False
        SECRET_KEY = "default_secret_key_change_in_production"
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/gold_fundamental")
        REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
        TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL")
        TELEGRAM_WEBAPP_URL = os.getenv("TELEGRAM_WEBAPP_URL")
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
        SESSION_ASIA_OPEN = "00:00"
        SESSION_LONDON_OPEN = "08:00"
        SESSION_NEW_YORK_OPEN = "13:00"
        DEFAULT_TIMEZONE = "UTC"
        MOCK_MODE = True

    settings = SettingsFallback()
