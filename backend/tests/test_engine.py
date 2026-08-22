import pytest
from app.engine.surprise_calculator import calculate_economic_surprise, parse_numeric_value
from app.engine.usd_engine import USDEngine
from app.engine.yield_engine import YieldEngine
from app.api.middleware.telegram_auth import verify_telegram_init_data
from app.schemas.llm import LLMAnalysisOutput


def test_parse_numeric_value():
    assert parse_numeric_value("0.2%") == 0.2
    assert parse_numeric_value("175K") == 175.0
    assert parse_numeric_value("$2485.50") == 2485.50
    assert parse_numeric_value(None) is None


def test_economic_surprise_cpi():
    # CPI actual below forecast -> dovish -> BULLISH Gold
    res = calculate_economic_surprise("0.2%", "0.3%", "INFLATION")
    assert res["surprise_val"] == -0.1
    assert res["surprise_direction"] == "BELOW_EXPECTATIONS"
    assert res["gold_impact"] == "BULLISH"


def test_economic_surprise_nfp():
    # NFP actual above forecast -> hawkish -> BEARISH Gold
    res = calculate_economic_surprise("220K", "175K", "EMPLOYMENT")
    assert res["surprise_val"] == 45.0
    assert res["surprise_direction"] == "ABOVE_EXPECTATIONS"
    assert res["gold_impact"] == "BEARISH"


def test_usd_engine():
    dxy_obs = {"value": 104.20, "change_pct": 0.35}
    res = USDEngine.evaluate_usd_state(dxy_obs, fed_stance="HAWKISH")
    assert res["usd_state"] == "STRONGER"
    assert res["gold_implication"] == "BEARISH"


def test_yield_engine():
    us10y_obs = {"value": 4.10, "change_pct": -0.5}
    real_yield_obs = {"value": 1.75, "change_pct": -0.8}
    res = YieldEngine.evaluate_yield_state(us10y_obs, real_yield_obs)
    assert res["yield_direction"] == "EASING"
    assert res["gold_impact"] == "BULLISH"


def test_telegram_auth_mock():
    user = verify_telegram_init_data("", "")
    assert user["first_name"] == "Demo"


def test_llm_pydantic_schema_validation():
    valid_json = {
        "bias": "BULLISH",
        "strength": "MODERATE",
        "main_driver": "Real yield decline following soft CPI.",
        "supporting_factors": ["Softer CPI", "Weaker USD"],
        "conflicting_factors": ["Resilient GDP"],
        "base_scenario": "Gold continues upward momentum.",
        "alternative_scenario": "PPI surprises to the upside.",
        "invalidation": "Real yield spike above 2.0%",
        "key_risks": ["Hawkish Fed speaker"],
        "next_catalyst": "NFP release",
        "risk_level": "MEDIUM"
    }
    model = LLMAnalysisOutput.model_validate(valid_json)
    assert model.bias == "BULLISH"
    assert model.strength == "MODERATE"
