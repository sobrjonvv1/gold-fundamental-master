from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from app.core.database import get_db
from app.collectors.forex_factory import ForexFactoryProvider
from app.collectors.mock_provider import MockFedProvider, MockMarketDataProvider, MockNewsProvider
from app.engine.fundamental_engine import FundamentalEngine

router = APIRouter(prefix="/gold", tags=["Gold Fundamentals"])
engine = FundamentalEngine()


@router.get("/current")
async def get_current_gold_fundamental(db: AsyncSession = Depends(get_db)):
    """
    Returns current main fundamental overview for XAUUSD across all 4 horizons.
    """
    ff_provider = ForexFactoryProvider()
    fed_provider = MockFedProvider()
    market_provider = MockMarketDataProvider()
    news_provider = MockNewsProvider()

    events = await ff_provider.fetch_events(None, None)
    fed_events = await fed_provider.fetch_fed_events()
    market_obs = await market_provider.fetch_market_observations()
    news = await news_provider.fetch_latest_news()

    # Analyze DAY horizon as default current view
    day_view = await engine.analyze_horizon("DAY", events, fed_events, market_obs, news)

    horizons_summary = [
        {"horizon": "MONTH", "bias": "BULLISH", "strength": "STRONG", "main_driver": "Central bank reserves + Real yields easing", "last_update": "2026-08-22T00:00:00Z"},
        {"horizon": "WEEK", "bias": "BULLISH", "strength": "MODERATE", "main_driver": "Dovish Fed speaker comments", "last_update": "2026-08-22T08:00:00Z"},
        {"horizon": "DAY", "bias": "NEUTRAL", "strength": "MODERATE", "main_driver": "Market digesting CPI data", "last_update": "2026-08-22T12:00:00Z"},
        {"horizon": "ASIA", "bias": "BULLISH", "strength": "WEAK", "main_driver": "Subdued yields in Tokyo session", "last_update": "2026-08-22T02:00:00Z"},
        {"horizon": "LONDON", "bias": "NEUTRAL", "strength": "MODERATE", "main_driver": "European bond market consolidation", "last_update": "2026-08-22T09:00:00Z"},
        {"horizon": "NEW_YORK", "bias": "BULLISH", "strength": "MODERATE", "main_driver": "US yields declining post-CPI", "last_update": "2026-08-22T14:00:00Z"},
    ]

    return {
        "instrument": "XAUUSD",
        "horizons": horizons_summary,
        "current_view": day_view,
        "drivers_summary": day_view["drivers_summary"],
        "data_quality": "GOOD"
    }


@router.get("/month")
async def get_month_horizon():
    return await engine.analyze_horizon("MONTH", [], [], {}, [])


@router.get("/week")
async def get_week_horizon():
    return await engine.analyze_horizon("WEEK", [], [], {}, [])


@router.get("/day")
async def get_day_horizon():
    return await engine.analyze_horizon("DAY", [], [], {}, [])


@router.get("/session")
async def get_session_horizon(name: str = Query("LONDON", description="Session name: ASIA, LONDON, NEW_YORK")):
    return await engine.analyze_horizon(f"SESSION_{name.upper()}", [], [], {}, [])


@router.get("/drivers")
async def get_drivers_summary():
    market_provider = MockMarketDataProvider()
    market_obs = await market_provider.fetch_market_observations()
    return {
        "USD": "WEAKER",
        "FED": "DOVISH",
        "REAL_YIELDS": "EASING",
        "INFLATION": "EASING",
        "MACRO": "RESILIENT",
        "GEOPOLITICS": "RISK_UP",
        "GOLD_DEMAND": "BULLISH",
        "market_data": market_obs
    }


@router.get("/history")
async def get_fundamental_history():
    return [
        {
            "timestamp": "2026-08-22T13:30:00Z",
            "horizon": "DAY",
            "previous_bias": "NEUTRAL",
            "new_bias": "BULLISH",
            "reason": "US Core CPI released below forecast at 0.2%, driving 10Y real yields down by 8 bps.",
            "trigger_event": "US Core CPI Release"
        },
        {
            "timestamp": "2026-08-21T18:00:00Z",
            "horizon": "WEEK",
            "previous_bias": "BEARISH",
            "new_bias": "NEUTRAL",
            "reason": "Powell comments at Economic Club signaled sensitivity to cooling inflation.",
            "trigger_event": "Fed Powell Speech"
        }
    ]
