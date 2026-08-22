import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import settings

logger = logging.getLogger("gold_fundamental.scheduler")
scheduler = AsyncIOScheduler()


async def scheduled_calendar_sync():
    logger.info("Running scheduled Economic Calendar Sync...")


async def scheduled_session_analysis(session_name: str):
    logger.info(f"Running scheduled session fundamental analysis for: {session_name}")


def start_scheduler():
    if not scheduler.running:
        # Schedule Asia, London, New York session analyses
        asia_h, asia_m = map(int, settings.SESSION_ASIA_OPEN.split(":"))
        london_h, london_m = map(int, settings.SESSION_LONDON_OPEN.split(":"))
        ny_h, ny_m = map(int, settings.SESSION_NEW_YORK_OPEN.split(":"))

        scheduler.add_job(scheduled_session_analysis, 'cron', hour=asia_h, minute=asia_m, args=["ASIA"], id="asia_session")
        scheduler.add_job(scheduled_session_analysis, 'cron', hour=london_h, minute=london_m, args=["LONDON"], id="london_session")
        scheduler.add_job(scheduled_session_analysis, 'cron', hour=ny_h, minute=ny_m, args=["NEW_YORK"], id="ny_session")
        
        # Periodic calendar sync every 15 mins
        scheduler.add_job(scheduled_calendar_sync, 'interval', minutes=15, id="calendar_sync")

        scheduler.start()
        logger.info("APScheduler background tasks initialized and started in UTC timezone.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped.")
