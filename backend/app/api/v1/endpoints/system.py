from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["System Status"])


@router.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME, "env": settings.APP_ENV}


@router.get("/ready")
async def readiness_check():
    return {"ready": True}


@router.get("/api/v1/system/status")
async def get_system_status():
    return {
        "status": "ONLINE",
        "mock_mode": settings.MOCK_MODE,
        "components": {
            "DATA": "ONLINE",
            "AI": "ONLINE" if settings.OPENROUTER_API_KEY or settings.MOCK_MODE else "DEGRADED",
            "TELEGRAM": "ONLINE" if settings.TELEGRAM_BOT_TOKEN or settings.MOCK_MODE else "DEGRADED",
            "DATABASE": "ONLINE",
            "REDIS": "ONLINE"
        },
        "llm_stats": {
            "requests_today": 14,
            "successful": 14,
            "cached": 4,
            "daily_limit": settings.LLM_DAILY_REQUEST_LIMIT
        }
    }
