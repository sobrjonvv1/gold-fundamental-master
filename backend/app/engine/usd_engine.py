from typing import Dict, Any, Optional


class USDEngine:
    @staticmethod
    def evaluate_usd_state(
        dxy_obs: Dict[str, Any],
        fed_stance: str = "NEUTRAL",
        geopolitics_risk: str = "NEUTRAL"
    ) -> Dict[str, Any]:
        """
        Evaluates USD State and underlying Macro Driver.
        Distinguishes between Hawkish Fed USD strength (bearish for Gold)
        vs Geopolitical Safe-Haven USD strength (can co-exist with bullish Gold).
        """
        dxy_val = dxy_obs.get("value", 100.0)
        dxy_change = dxy_obs.get("change_pct", 0.0)

        usd_state = "NEUTRAL"
        if dxy_change > 0.15:
            usd_state = "STRONGER"
        elif dxy_change < -0.15:
            usd_state = "WEAKER"

        # Determine macro driver
        driver = "Market positioning & cross-currency rebalancing"
        gold_implication = "NEUTRAL"

        if usd_state == "STRONGER":
            if fed_stance in ["HAWKISH", "MORE_HAWKISH"]:
                driver = "Hawkish Fed policy rate expectations strengthening USD"
                gold_implication = "BEARISH" # Headwind for Gold
            elif geopolitics_risk in ["RISK_UP", "CRITICAL"]:
                driver = "Global safe-haven demand driving USD inflows"
                gold_implication = "NEUTRAL" # Gold also bids up as safe haven
            else:
                driver = "US macro outperformance relative to major currencies"
                gold_implication = "MODERATE_BEARISH"
        elif usd_state == "WEAKER":
            if fed_stance in ["DOVISH", "MORE_DOVISH"]:
                driver = "Dovish Fed rate-cut expectations depressing USD"
                gold_implication = "BULLISH" # Direct tailwind for Gold
            else:
                driver = "Improving global risk sentiment and capital outflows from USD"
                gold_implication = "MODERATE_BULLISH"

        return {
            "usd_state": usd_state,
            "dxy_value": dxy_val,
            "dxy_change_pct": dxy_change,
            "driver": driver,
            "gold_implication": gold_implication
        }
