"""Live, traceable context for XAU/USD fundamental reports."""
from __future__ import annotations
import csv
import io
import logging
from datetime import datetime, timezone
from typing import Any
import httpx
from app.collectors.forex_factory import ForexFactoryProvider
from app.collectors.mock_provider import MockFedProvider, MockMarketDataProvider, MockNewsProvider
from app.core.config import settings
logger = logging.getLogger("gold_fundamental.live_context")
FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFII10,DTWEXBGS"
YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1d"

async def _fred(client: httpx.AsyncClient) -> dict[str, dict[str, Any]]:
    response = await client.get(FRED_CSV)
    response.raise_for_status()
    rows = list(csv.DictReader(io.StringIO(response.text)))
    usable = [r for r in rows if r.get("DFII10") not in (None, ".") and r.get("DTWEXBGS") not in (None, ".")]
    if len(usable) < 2:
        raise ValueError("FRED returned insufficient observations")
    current, previous, now = usable[-1], usable[-2], datetime.now(timezone.utc).isoformat()
    real_yield, old_real = float(current["DFII10"]), float(previous["DFII10"])
    dxy, old_dxy = float(current["DTWEXBGS"]), float(previous["DTWEXBGS"])
    return {
        "REAL_YIELD": {"instrument": "REAL_YIELD", "value": real_yield, "change_pct": round((real_yield-old_real)/old_real*100, 3), "direction": "UP" if real_yield > old_real else "DOWN", "driver": "10Y TIPS real yield (FRED DFII10)", "timestamp": now, "source": "FRED", "source_url": "https://fred.stlouisfed.org/series/DFII10"},
        "DXY": {"instrument": "DXY", "value": dxy, "change_pct": round((dxy-old_dxy)/old_dxy*100, 3), "direction": "UP" if dxy > old_dxy else "DOWN", "driver": "Trade-weighted US dollar index (FRED DTWEXBGS)", "timestamp": now, "source": "FRED", "source_url": "https://fred.stlouisfed.org/series/DTWEXBGS"},
    }

async def _yahoo(client: httpx.AsyncClient, symbol: str, instrument: str) -> dict[str, Any]:
    response = await client.get(YAHOO_URL.format(symbol=symbol), headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    data = response.json()["chart"]["result"][0]
    closes = [x for x in data["indicators"]["quote"][0]["close"] if x is not None]
    if len(closes) < 2:
        raise ValueError(f"No price for {instrument}")
    value, old = closes[-1], closes[-2]
    return {"instrument": instrument, "value": round(value, 4), "change_pct": round((value-old)/old*100, 3), "direction": "UP" if value > old else "DOWN", "driver": f"Daily market close ({instrument})", "timestamp": datetime.now(timezone.utc).isoformat(), "source": "Yahoo Finance", "source_url": f"https://finance.yahoo.com/quote/{symbol}"}

async def collect_context() -> tuple[list[dict], list[dict], dict[str, dict], list[dict], str, list[dict]]:
    """Facts first: failures lower quality; they never become invented data."""
    if settings.MOCK_MODE:
        return (await ForexFactoryProvider().fetch_events(None, None), await MockFedProvider().fetch_fed_events(), await MockMarketDataProvider().fetch_market_observations(), await MockNewsProvider().fetch_latest_news(), "MOCK", [])
    market: dict[str, dict] = {}
    sources, failures = [], []
    async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
        for name, request in (("FRED", _fred(client)), ("XAUUSD", _yahoo(client, "GC=F", "XAUUSD")), ("US10Y", _yahoo(client, "^TNX", "US10Y"))):
            try:
                result = await request
                if name == "FRED":
                    market.update(result)
                else:
                    market[name] = result
                sources.append({"name": name, "status": "OK"})
            except Exception as exc:
                failures.append(name)
                logger.warning("Live source %s failed: %s", name, type(exc).__name__)
    events = await ForexFactoryProvider().fetch_events(None, None)
    return events, [], market, [], ("LIVE" if len(market) >= 3 and not failures else "DEGRADED"), sources
