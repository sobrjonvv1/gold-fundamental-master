import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.middleware.rate_limit import RateLimitMiddleware
from app.core.config import settings, validate_production_settings
from app.core.database import engine
from app.core.logging import logger
from app.core.redis import close_redis
from app.api.v1.router import api_router
from app.api.v1.endpoints.system import router as system_router
from app.services.scheduler_service import start_scheduler, stop_scheduler
from app.services.telegram_service import run_telegram_bot


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_production_settings()
    logger.info(f"Starting {settings.PROJECT_NAME} in {settings.APP_ENV} mode (MOCK_MODE={settings.MOCK_MODE})")
    if settings.SCHEDULER_ENABLED:
        start_scheduler()
    bot_task = None
    if settings.TELEGRAM_POLLING_ENABLED:
        bot_task = asyncio.create_task(run_telegram_bot(), name="telegram-polling")
    try:
        yield
    finally:
        if bot_task is not None:
            bot_task.cancel()
            with suppress(asyncio.CancelledError):
                await bot_task
        if settings.SCHEDULER_ENABLED:
            stop_scheduler()
        await close_redis()
        await engine.dispose()
        logger.info(f"Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Fundamental Analysis Engine & API for Gold (XAU/USD)",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)

# Include Routers
app.include_router(system_router)
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
