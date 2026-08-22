from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import check_database_connection
from app.core.redis import check_redis_connection
from app.services.telegram_service import status_snapshot

router = APIRouter(tags=["System Status"])


async def collect_system_status() -> dict:
    database_ok, database_status = await check_database_connection()
    _, redis_status = await check_redis_connection()
    telegram = status_snapshot()
    data_status = "MOCK" if settings.MOCK_MODE else "DEGRADED"
    ai_status = "MOCK" if settings.MOCK_MODE else ("CONFIGURED" if settings.OPENROUTER_API_KEY else "OFFLINE")

    components = {
        "DATA": data_status,
        "AI": ai_status,
        "TELEGRAM": telegram["status"],
        "DATABASE": database_status,
        "REDIS": redis_status,
    }
    required_ok = database_ok and (
        not settings.TELEGRAM_POLLING_ENABLED or telegram["status"] == "ONLINE"
    )
    return {
        "status": "ONLINE" if required_ok else "DEGRADED",
        "mode": "MOCK" if settings.MOCK_MODE else "LIVE",
        "mock_mode": settings.MOCK_MODE,
        "components": components,
        "details": {"TELEGRAM": telegram["detail"]},
        "redis_optional": True,
    }


@router.get("/health")
async def health_check():
    """Liveness only; use /ready for dependency readiness."""
    return {"status": "ok", "app": settings.PROJECT_NAME, "env": settings.APP_ENV}


@router.get("/ready")
async def readiness_check():
    status = await collect_system_status()
    return JSONResponse(status_code=200 if status["status"] == "ONLINE" else 503, content=status)


@router.get("/api/v1/system/status")
async def get_system_status():
    return await collect_system_status()
