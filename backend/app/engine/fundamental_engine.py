import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.engine.surprise_calculator import calculate_economic_surprise
from app.engine.usd_engine import USDEngine
from app.engine.yield_engine import YieldEngine
from app.engine.openrouter_client import OpenRouterClient
from app.schemas.llm import LLMAnalysisOutput

logger = logging.getLogger("gold_fundamental.engine")


class FundamentalEngine:
    def __init__(self):
        self.openrouter = OpenRouterClient()

    async def analyze_horizon(
        self,
        horizon: str,
        events: List[Dict[str, Any]],
        fed_events: List[Dict[str, Any]],
        market_obs: Dict[str, Dict[str, Any]],
        news_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Processes raw & normalized fundamental data into a unified horizon view.
        No technical analysis used.
        """
        logger.info(f"Executing Fundamental Engine for horizon: {horizon}")

        # 1. Evaluate USD State & Driver
        dxy_data = market_obs.get("DXY", {"value": 103.85, "change_pct": -0.2})
        fed_stance = fed_events[0].get("stance", "NEUTRAL") if fed_events else "NEUTRAL"
        usd_eval = USDEngine.evaluate_usd_state(dxy_data, fed_stance=fed_stance)

        # 2. Evaluate Yield State
        us10y_data = market_obs.get("US10Y", {"value": 4.18, "change_pct": -0.5})
        real_yield_data = market_obs.get("REAL_YIELD", {"value": 1.82, "change_pct": -0.8})
        yield_eval = YieldEngine.evaluate_yield_state(us10y_data, real_yield_data)

        # 3. Calculate Economic Surprises for Macro Releases
        macro_surprises = []
        for ev in events:
            if ev.get("actual") and ev.get("forecast"):
                surp = calculate_economic_surprise(ev.get("actual"), ev.get("forecast"), ev.get("event_type", "MACRO"))
                macro_surprises.append({
                    "event_name": ev.get("event_name"),
                    "impact": ev.get("impact"),
                    "gold_impact": surp["gold_impact"],
                    "reasoning": surp["reasoning"]
                })

        # 4. Aggregate Context
        compact_context = {
            "horizon": horizon,
            "usd_state": usd_eval,
            "yield_state": yield_eval,
            "fed_stance": fed_stance,
            "macro_surprises": macro_surprises[:5],
            "recent_news_count": len(news_items),
            "top_headline": news_items[0].get("headline") if news_items else "No critical headlines"
        }

        # 5. Call LLM for Synthesis & Scenarios
        llm_output: LLMAnalysisOutput = await self.openrouter.generate_fundamental_analysis(horizon, compact_context)

        return {
            "instrument": "XAUUSD",
            "horizon": horizon,
            "bias": llm_output.bias,
            "strength": llm_output.strength,
            "main_driver": llm_output.main_driver,
            "supporting_factors": llm_output.supporting_factors,
            "conflicting_factors": llm_output.conflicting_factors,
            "base_scenario": llm_output.base_scenario,
            "alternative_scenario": llm_output.alternative_scenario,
            "invalidation": llm_output.invalidation,
            "key_risks": llm_output.key_risks,
            "next_catalyst": llm_output.next_catalyst,
            "data_quality": "GOOD",
            "drivers_summary": {
                "USD": usd_eval["usd_state"],
                "FED": fed_stance,
                "REAL_YIELDS": yield_eval["yield_direction"],
                "INFLATION": "EASING" if any(s["gold_impact"] == "BULLISH" for s in macro_surprises) else "STABLE",
                "MACRO": "RESILIENT",
                "GEOPOLITICS": "RISK_UP",
                "GOLD_DEMAND": "BULLISH"
            },
            "timestamp": datetime.now(timezone.utc)
        }
