from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from app.collectors.base import (
    BaseEconomicCalendarProvider,
    BaseFedProvider,
    BaseMarketDataProvider,
    BaseNewsProvider,
)


class MockEconomicCalendarProvider(BaseEconomicCalendarProvider):
    async def fetch_events(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return [
            {
                "event_name": "US Core CPI (MoM)",
                "event_type": "INFLATION",
                "currency": "USD",
                "country": "US",
                "event_time": (now - timedelta(hours=2)).isoformat(),
                "impact": "HIGH",
                "actual": "0.2%",
                "forecast": "0.3%",
                "previous": "0.3%",
                "previous_revision": None,
                "surprise_val": -0.33,
                "gold_impact": "BULLISH",
                "source_url": "https://www.forexfactory.com/calendar",
                "provider": "forex_factory_mock"
            },
            {
                "event_name": "Non-Farm Employment Change (NFP)",
                "event_type": "EMPLOYMENT",
                "currency": "USD",
                "country": "US",
                "event_time": (now + timedelta(days=2)).isoformat(),
                "impact": "HIGH",
                "actual": None,
                "forecast": "175K",
                "previous": "206K",
                "previous_revision": "218K",
                "surprise_val": None,
                "gold_impact": "NEUTRAL",
                "source_url": "https://www.forexfactory.com/calendar",
                "provider": "forex_factory_mock"
            },
            {
                "event_name": "FOMC Press Conference",
                "event_type": "FED",
                "currency": "USD",
                "country": "US",
                "event_time": (now + timedelta(days=5)).isoformat(),
                "impact": "HIGH",
                "actual": None,
                "forecast": None,
                "previous": None,
                "previous_revision": None,
                "surprise_val": None,
                "gold_impact": "NEUTRAL",
                "source_url": "https://www.forexfactory.com/calendar",
                "provider": "forex_factory_mock"
            }
        ]


class MockFedProvider(BaseFedProvider):
    async def fetch_fed_events(self) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return [
            {
                "event_title": "Powell Speech at Economic Club",
                "speaker_or_type": "Powell",
                "event_time": (now - timedelta(hours=12)).isoformat(),
                "stance": "DOVISH",
                "summary": "Powell noted that progress on disinflation is continuing and labor market cooling reduces upside inflation risk.",
                "source_url": "https://www.federalreserve.gov"
            },
            {
                "event_title": "FOMC Statement Release",
                "speaker_or_type": "FOMC",
                "event_time": (now - timedelta(days=10)).isoformat(),
                "stance": "NEUTRAL",
                "summary": "Policy rate maintained at target range. Committee seeks greater confidence before initiating rate reductions.",
                "source_url": "https://www.federalreserve.gov"
            }
        ]


class MockMarketDataProvider(BaseMarketDataProvider):
    async def fetch_market_observations(self) -> Dict[str, Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return {
            "DXY": {
                "instrument": "DXY",
                "value": 103.85,
                "change_pct": -0.35,
                "direction": "DOWN",
                "driver": "Dovish Fed repricing after softer CPI",
                "timestamp": now.isoformat(),
                "source": "mock_market_data"
            },
            "US10Y": {
                "instrument": "US10Y",
                "value": 4.18,
                "change_pct": -0.62,
                "direction": "DOWN",
                "driver": "Lower inflation expectations easing nominal yields",
                "timestamp": now.isoformat(),
                "source": "mock_market_data"
            },
            "REAL_YIELD": {
                "instrument": "REAL_YIELD",
                "value": 1.82,
                "change_pct": -0.85,
                "direction": "DOWN",
                "driver": "Falling 10Y TIPS yield directly supporting Gold",
                "timestamp": now.isoformat(),
                "source": "mock_market_data"
            },
            "XAUUSD": {
                "instrument": "XAUUSD",
                "value": 2485.50,
                "change_pct": 0.75,
                "direction": "UP",
                "driver": "Fundamental tailwinds from lower real yield and softer USD",
                "timestamp": now.isoformat(),
                "source": "mock_market_data"
            }
        }


class MockNewsProvider(BaseNewsProvider):
    async def fetch_latest_news(self) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return [
            {
                "headline": "US Inflation Cools More Than Expected as Housing Costs Soften",
                "body": "Core CPI slowed to 0.2% monthly, reinforcing expectations for upcoming Federal Reserve interest rate cuts.",
                "source": "Reuters",
                "source_url": "https://www.reuters.com/markets/us-cpi-data",
                "published_at": (now - timedelta(hours=2)).isoformat(),
                "gold_relevance": "HIGH",
                "impact_bias": "BULLISH",
                "ai_summary": "Soft CPI lowers real yields and weakens USD, strong fundamental bullish driver for XAU/USD.",
                "content_hash": "cpi_soft_news_hash_102"
            },
            {
                "headline": "Middle East Diplomatic Talks Progress Amid Regional Ceasefire Draft",
                "body": "Delegates report preliminary agreement on de-escalation steps in Middle East proxy conflicts.",
                "source": "Bloomberg",
                "source_url": "https://www.bloomberg.com/news/middle-east",
                "published_at": (now - timedelta(hours=6)).isoformat(),
                "gold_relevance": "MEDIUM",
                "impact_bias": "BEARISH",
                "ai_summary": "Geopolitical risk premium slightly unwinds as diplomatic de-escalation progress is reported.",
                "content_hash": "geopolitics_middle_east_hash_204"
            }
        ]
