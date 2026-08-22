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

        # Attempt to scrape/fetch from configured external URL or API
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://nws.forexfactory.com/news/get_calendar.php",
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                )
                if response.status_code == 200:
                    raw_data = response.json()
                    events = self._parse_ff_json(raw_data, start_time, end_time)
                    # Cache in Redis
                    try:
                        redis = await get_redis()
                        await redis.set(self.cache_key, json.dumps(events), ex=3600)
                    except Exception as re:
                        logger.warning(f"Failed to cache Forex Factory events in Redis: {re}")
                    return events
                else:
                    logger.error(f"Forex Factory API returned HTTP status {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching Forex Factory calendar data: {e}. Falling back to cache/mock.")

        # Fallback 1: Try Redis Cache
        try:
            redis = await get_redis()
            cached = await redis.get(self.cache_key)
            if cached:
                logger.info("Returning cached Forex Factory calendar events from Redis")
                return json.loads(cached)
        except Exception as ce:
            logger.warning(f"Error reading Redis cache: {ce}")

        # Fallback 2: Mock provider
        logger.info("Falling back to Mock Economic Calendar provider")
        return await self.mock_fallback.fetch_events(start_time, end_time)

    def _parse_ff_json(self, raw_events: List[Dict[str, Any]], start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        parsed = []
        for item in raw_events:
            try:
                currency = item.get("country", "")
                if currency != "USD":
                    continue # Focus on USD macro events for Gold
                
                impact = item.get("impact", "LOW").upper()
                event_name = item.get("title", "Economic Event")
                event_time_str = item.get("date", "")
                
                parsed.append({
                    "event_name": event_name,
                    "event_type": self._classify_event_type(event_name),
                    "currency": currency,
                    "country": "US",
                    "event_time": event_time_str,
                    "impact": impact,
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
        elif "payrolls" in t or "nfp" in t or "unemployment" in t or "jobless" in t:
            return "EMPLOYMENT"
        elif "gdp" in t or "pmi" in t or "ism" in t or "retail sales" in t:
            return "GROWTH"
        elif "fed" in t or "fomc" in t or "powell" in t:
            return "FED"
        return "MACRO"
