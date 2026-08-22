import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from app.core.config import settings

logger = logging.getLogger("gold_fundamental.scheduler")
scheduler = AsyncIOScheduler(timezone=timezone(settings.DEFAULT_TIMEZONE))


async def scheduled_calendar_sync():
    logger.info("Running scheduled Economic Calendar Sync...")


async def scheduled_session_analysis(session_name: str):
    logger.info(f"Running scheduled session fundamental analysis for: {session_name}")


def start_scheduler():
    if scheduler.running:
        return
    try:
        # Schedule Asia, London, New York session analyses
        asia_h, asia_m = map(int, settings.SESSION_ASIA_OPEN.split(":"))
        london_h, london_m = map(int, settings.SESSION_LONDON_OPEN.split(":"))
        ny_h, ny_m = map(int, settings.SESSION_NEW_YORK_OPEN.split(":"))

        scheduler.add_job(scheduled_session_analysis, 'cron', hour=asia_h, minute=asia_m, args=["ASIA"], id="asia_session", replace_existing=True)
        scheduler.add_job(scheduled_session_analysis, 'cron', hour=london_h, minute=london_m, args=["LONDON"], id="london_session", replace_existing=True)
        scheduler.add_job(scheduled_session_analysis, 'cron', hour=ny_h, minute=ny_m, args=["NEW_YORK"], id="ny_session", replace_existing=True)
        
        # Periodic calendar sync every 15 mins
        scheduler.add_job(scheduled_calendar_sync, 'interval', minutes=15, id="calendar_sync", replace_existing=True)

        scheduler.start()
        logger.info("APScheduler background tasks initialized and started in %s timezone.", settings.DEFAULT_TIMEZONE)
    except Exception:
        logger.exception("APScheduler failed to start; scheduled jobs are disabled")


def stop_scheduler():
    try:
        if scheduler.running:
            scheduler.shutdown(wait=False)
            logger.info("APScheduler stopped.")
    except Exception:
        logger.exception("APScheduler failed to stop cleanly")
