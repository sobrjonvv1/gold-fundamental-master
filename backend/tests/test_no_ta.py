import os
import re
import pytest

FORBIDDEN_TA_PATTERNS = [
    r"\brsi\b", r"\bmacd\b", r"\bema\b", r"\bsma\b", r"\bvwap\b", r"\batr\b",
    r"\bsupport_level\b", r"\bresistance_level\b", r"\bcandlestick\b",
    r"\bmarket_structure\b", r"\border_block\b", r"\borderblock\b", r"\bliquidity_pool\b",
    r"\btechnical_indicator\b", r"\btechnical_entry\b", r"\bstop_loss\b", r"\btake_profit\b"
]


def test_no_technical_analysis_in_backend():
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
    
    found_violations = []
    for root, _, files in os.walk(backend_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().lower()
                    for pattern in FORBIDDEN_TA_PATTERNS:
                        if re.search(pattern, content):
                            if "openrouter_client.py" in file:
                                continue
                            found_violations.append(f"Forbidden TA pattern '{pattern}' found in {filepath}")

    assert len(found_violations) == 0, f"Technical Analysis code detected! Violations:\n" + "\n".join(found_violations)
