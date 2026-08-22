import httpx
import logging
import hashlib
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.domain import Alert

logger = logging.getLogger("gold_fundamental.alerts")


class AlertService:
    @staticmethod
    def generate_hash(content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    @classmethod
    async def send_alert_if_new(
        self,
        db: AsyncSession,
        alert_type: str,
        title: str,
        message: str,
        horizon: Optional[str] = None
    ) -> bool:
        content_hash = self.generate_hash(f"{alert_type}:{title}:{message}")

        # Check for duplicates in DB
        stmt = select(Alert).where(Alert.event_hash == content_hash)
        res = await db.execute(stmt)
        if res.scalar_one_or_none():
            logger.info(f"Duplicate alert suppressed: [{alert_type}] {title}")
            return False

        # Save to DB
        new_alert = Alert(
            alert_type=alert_type,
            title=title,
            message=message,
            event_hash=content_hash,
            horizon=horizon
        )
        db.add(new_alert)
        await db.commit()

        # Broadcast via Telegram Bot API if token configured
        if settings.TELEGRAM_BOT_TOKEN and not settings.MOCK_MODE:
            await self._broadcast_telegram(f"<b>[{alert_type}] {title}</b>\n\n{message}")

        logger.info(f"Alert sent successfully: [{alert_type}] {title}")
        return True

    @classmethod
    async def _broadcast_telegram(cls, formatted_html: str):
        # Implementation for Telegram broadcasting
        pass
