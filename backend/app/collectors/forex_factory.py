import httpx
import logging
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.collectors.base import BaseEconomicCalendarProvider
from app.collectors.mock_provider import MockEconomicCalendarProvider
from app.core.config import settings
from app.core.redis import get_redis

logger = logging.getLogger("gold_fundamental.forex_factory")


class ForexFactoryProvider(BaseEconomicCalendarProvider):
    def __init__(self):
        self.mock_fallback = MockEconomicCalendarProvider()
        self.cache_key = "cache:forex_factory:events"

    async def fetch_events(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        if settings.MOCK_MODE or settings.FOREX_FACTORY_PROVIDER == "mock":
            logger.info("Using Mock Forex Factory provider (MOCK_MODE=True)")
            return await self.mock_fallback.fetch_events(start_time, end_time)

        # Attempt to fetch the public Forex Factory calendar.
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://nws.forexfactory.com/news/get_calendar.php",
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                )
                if response.status_code == 200:
                    raw_data = response.json()
                    events = self._parse_ff_json(raw_data, start_time, end_time)
                    try:
                        redis = await get_redis()
                        await redis.set(self.cache_key, json.dumps(events), ex=3600)
                    except Exception as re:
                        logger.warning(f"Failed to cache Forex Factory events in Redis: {re}")
                    return events
                logger.error(f"Forex Factory API returned HTTP status {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching Forex Factory calendar data: {e}. Falling back to cache only.")

        # A recent cache is still factual. In live mode, never replace it with synthetic events.
        try:
            redis = await get_redis()
            cached = await redis.get(self.cache_key)
            if cached:
                logger.info("Returning cached Forex Factory calendar events from Redis")
                return json.loads(cached)
        except Exception as ce:
            logger.warning(f"Error reading Redis cache: {ce}")

        logger.warning("No live Forex Factory events or cache are available; returning no events")
        return []

    def _parse_ff_json(self, raw_events: List[Dict[str, Any]], start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        parsed = []
        for item in raw_events:
            try:
                currency = item.get("country", "")
                if currency != "USD":
                    continue

                event_name = item.get("title", "Economic Event")
                parsed.append({
                    "event_name": event_name,
                    "event_type": self._classify_event_type(event_name),
                    "currency": currency,
                    "country": "US",
                    "event_time": item.get("date", ""),
                    "impact": item.get("impact", "LOW").upper(),
                    "actual": item.get("actual", ""),
                    "forecast": item.get("forecast", ""),
                    "previous": item.get("previous", ""),
                    "previous_revision": None,
                    "surprise_val": None,
                    "gold_impact": "NEUTRAL",
                    "source_url": "https://www.forexfactory.com/calendar",
                    "provider": "forex_factory"
                })
            except Exception:
                continue
        return parsed

    def _classify_event_type(self, title: str) -> str:
        t = title.lower()
        if "cpi" in t or "pce" in t or "ppi" in t or "inflation" in t:
            return "INFLATION"
        if "payrolls" in t or "nfp" in t or "unemployment" in t or "jobless" in t:
            return "EMPLOYMENT"
        if "gdp" in t or "pmi" in t or "ism" in t or "retail sales" in t:
            return "GROWTH"
        if "fed" in t or "fomc" in t or "powell" in t:
            return "FED"
        return "MACRO"
