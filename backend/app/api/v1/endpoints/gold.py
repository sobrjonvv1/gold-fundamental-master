from typing import Any, Dict, List, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.collectors.live_context import collect_context
from app.engine.fundamental_engine import FundamentalEngine

router = APIRouter(prefix="/gold", tags=["Gold Fundamentals"])
engine = FundamentalEngine()


@router.get("/current")
async def get_current_gold_fundamental(db: AsyncSession = Depends(get_db)):
    """
    Returns current main fundamental overview for XAUUSD across all 4 horizons.
    """
    events, fed_events, market_obs, news, quality, sources = await collect_context()

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
        "data_quality": quality,
        "sources": sources,
    }


@router.get("/month")
async def get_month_horizon():
    events, fed_events, market_obs, news, _, _ = await collect_context()
    return await engine.analyze_horizon("MONTH", events, fed_events, market_obs, news)


@router.get("/week")
async def get_week_horizon():
    events, fed_events, market_obs, news, _, _ = await collect_context()
    return await engine.analyze_horizon("WEEK", events, fed_events, market_obs, news)


@router.get("/day")
async def get_day_horizon():
    events, fed_events, market_obs, news, _, _ = await collect_context()
    return await engine.analyze_horizon("DAY", events, fed_events, market_obs, news)


@router.get("/session")
async def get_session_horizon(
    name: Literal["ASIA", "LONDON", "NEW_YORK"] = Query(
        "LONDON", description="Session name: ASIA, LONDON, NEW_YORK"
    )
):
    events, fed_events, market_obs, news, _, _ = await collect_context()
    return await engine.analyze_horizon(f"SESSION_{name}", events, fed_events, market_obs, news)


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
