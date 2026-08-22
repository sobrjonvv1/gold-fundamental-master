import re
from typing import Optional, Dict, Any


def parse_numeric_value(val_str: Optional[str]) -> Optional[float]:
    if not val_str:
        return None
    # Remove %, K, M, B, $, commas
    cleaned = re.sub(r'[^\d\.\-\+]', '', val_str)
    try:
        return float(cleaned)
    except ValueError:
        return None


def calculate_economic_surprise(actual_str: Optional[str], forecast_str: Optional[str], event_type: str = "MACRO") -> Dict[str, Any]:
    """
    Calculates numerical & qualitative economic surprise.
    Example: CPI Actual < Forecast => Inflation surprise negative => Dovish Fed expectation => BULLISH Gold.
    NFP Actual > Forecast => Stronger growth/labor => Hawkish Fed expectation => BEARISH Gold.
    """
    actual_num = parse_numeric_value(actual_str)
    forecast_num = parse_numeric_value(forecast_str)

    if actual_num is None or forecast_num is None:
        return {
            "surprise_val": 0.0,
            "surprise_direction": "NONE",
            "gold_impact": "NEUTRAL",
            "reasoning": "Missing actual or forecast data"
        }

    diff = actual_num - forecast_num
    surprise_direction = "ABOVE_EXPECTATIONS" if diff > 0 else ("BELOW_EXPECTATIONS" if diff < 0 else "IN_LINE")

    # Context-aware interpretation for Gold
    gold_impact = "NEUTRAL"
    reasoning = f"Actual ({actual_str}) vs Forecast ({forecast_str})"

    if event_type in ["INFLATION", "CPI", "PCE", "PPI"]:
        if diff > 0:
            gold_impact = "BEARISH"
            reasoning = "Higher inflation supports higher real yields and a more hawkish Fed, pressuring Gold."
        elif diff < 0:
            gold_impact = "BULLISH"
            reasoning = "Softer inflation eases rate expectations and real yields, supporting Gold."
    elif event_type in ["EMPLOYMENT", "NFP", "JOBS"]:
        if diff > 0:
            gold_impact = "BEARISH"
            reasoning = "Strong employment reduces urgency for rate cuts, bolstering USD & yields."
        elif diff < 0:
            gold_impact = "BULLISH"
            reasoning = "Weak labor market increases rate cut expectations, weakening USD."
    elif event_type in ["GROWTH", "GDP", "PMI", "RETAIL_SALES"]:
        if diff > 0:
            gold_impact = "BEARISH"
            reasoning = "Robust economic growth lowers recession risk and rate-cut odds."
        elif diff < 0:
            gold_impact = "BULLISH"
            reasoning = "Economic slowing fuels rate-cut expectations and safe-haven interest."

    return {
        "surprise_val": round(diff, 4),
        "surprise_direction": surprise_direction,
        "gold_impact": gold_impact,
        "reasoning": reasoning
    }
