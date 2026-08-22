from typing import Dict, Any


class YieldEngine:
    @staticmethod
    def evaluate_yield_state(
        us10y_obs: Dict[str, Any],
        real_yield_obs: Dict[str, Any],
        cpi_surprise: float = 0.0
    ) -> Dict[str, Any]:
        """
        Evaluates Treasury Yields and Real Yields (TIPS).
        Real Yield = Nominal Yield - Inflation Expectations.
        Gold has a strong inverse fundamental relationship with Real Yields.
        """
        real_yield_val = real_yield_obs.get("value", 1.80)
        real_yield_change = real_yield_obs.get("change_pct", 0.0)
        us10y_val = us10y_obs.get("value", 4.20)

        yield_direction = "STABLE"
        if real_yield_change < -0.30:
            yield_direction = "EASING"
        elif real_yield_change > 0.30:
            yield_direction = "TIGHTENING"

        gold_impact = "NEUTRAL"
        driver = "TIPS market yield dynamics"

        if yield_direction == "EASING":
            gold_impact = "BULLISH"
            driver = "Falling real yields reduce opportunity cost of holding Gold"
        elif yield_direction == "TIGHTENING":
            gold_impact = "BEARISH"
            driver = "Rising real yields increase opportunity cost of non-yielding Gold"

        return {
            "real_yield_value": real_yield_val,
            "real_yield_change_pct": real_yield_change,
            "us10y_value": us10y_val,
            "yield_direction": yield_direction,
            "driver": driver,
            "gold_impact": gold_impact
        }
