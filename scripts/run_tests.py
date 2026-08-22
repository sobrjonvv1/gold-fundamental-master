import os
import re
import sys
import unittest

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_path)

from app.engine.surprise_calculator import calculate_economic_surprise, parse_numeric_value
from app.engine.usd_engine import USDEngine
from app.engine.yield_engine import YieldEngine
from app.api.middleware.telegram_auth import verify_telegram_init_data


class TestGoldFundamentalMaster(unittest.TestCase):
    def test_parse_numeric_value(self):
        self.assertEqual(parse_numeric_value("0.2%"), 0.2)
        self.assertEqual(parse_numeric_value("175K"), 175.0)
        self.assertEqual(parse_numeric_value("$2485.50"), 2485.50)
        self.assertIsNone(parse_numeric_value(None))

    def test_cpi_surprise_calculation(self):
        res = calculate_economic_surprise("0.2%", "0.3%", "INFLATION")
        self.assertEqual(res["surprise_val"], -0.1)
        self.assertEqual(res["surprise_direction"], "BELOW_EXPECTATIONS")
        self.assertEqual(res["gold_impact"], "BULLISH")

    def test_nfp_surprise_calculation(self):
        res = calculate_economic_surprise("220K", "175K", "EMPLOYMENT")
        self.assertEqual(res["surprise_val"], 45.0)
        self.assertEqual(res["surprise_direction"], "ABOVE_EXPECTATIONS")
        self.assertEqual(res["gold_impact"], "BEARISH")

    def test_usd_engine(self):
        dxy_obs = {"value": 104.20, "change_pct": 0.35}
        res = USDEngine.evaluate_usd_state(dxy_obs, fed_stance="HAWKISH")
        self.assertEqual(res["usd_state"], "STRONGER")
        self.assertEqual(res["gold_implication"], "BEARISH")

    def test_yield_engine(self):
        us10y_obs = {"value": 4.10, "change_pct": -0.5}
        real_yield_obs = {"value": 1.75, "change_pct": -0.8}
        res = YieldEngine.evaluate_yield_state(us10y_obs, real_yield_obs)
        self.assertEqual(res["yield_direction"], "EASING")
        self.assertEqual(res["gold_impact"], "BULLISH")

    def test_telegram_auth_mock(self):
        user = verify_telegram_init_data("", "")
        self.assertEqual(user["first_name"], "Demo")

    def test_no_technical_analysis_in_backend(self):
        # Strict TA indicator word boundary checks
        FORBIDDEN_TA_PATTERNS = [
            r"\brsi\b", r"\bmacd\b", r"\bema\b", r"\bsma\b", r"\bvwap\b", r"\batr\b",
            r"\bsupport_level\b", r"\bresistance_level\b", r"\bcandlestick\b",
            r"\bmarket_structure\b", r"\border_block\b", r"\borderblock\b", r"\bliquidity_pool\b",
            r"\btechnical_indicator\b", r"\btechnical_entry\b", r"\bstop_loss\b", r"\btake_profit\b"
        ]
        backend_dir = os.path.join(backend_path, "app")
        violations = []
        for root, _, files in os.walk(backend_dir):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().lower()
                        for pattern in FORBIDDEN_TA_PATTERNS:
                            if re.search(pattern, content):
                                # Ignore explicit prompt instruction context where LLM is instructed NOT to use technical indicators
                                matches = re.findall(pattern, content)
                                if "openrouter_client.py" in file and ("rsi" in matches or "macd" in matches or "candlestick" in matches):
                                    continue
                                violations.append(f"Forbidden TA pattern '{pattern}' found in {filepath}")
        self.assertEqual(len(violations), 0, f"TA terms found: {violations}")


if __name__ == "__main__":
    unittest.main()
