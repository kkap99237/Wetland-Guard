"""
tests/test_risk.py
Tests for risk scoring, communication thresholds, and evidence reason generation.
"""
import pandas as pd
import pytest
from src.risk import compute_risk_score, categorize_risk
from src.explanations import generate_reason_codes


def test_risk_score_conversion():
    assert compute_risk_score(0.854) == 85.4
    assert compute_risk_score(0.0) == 0.0
    assert compute_risk_score(1.0) == 100.0


def test_risk_categorization():
    assert categorize_risk(25.0) == "LOW"
    assert categorize_risk(34.9) == "LOW"
    assert categorize_risk(35.0) == "MEDIUM"
    assert categorize_risk(69.9) == "MEDIUM"
    assert categorize_risk(70.0) == "HIGH"
    assert categorize_risk(95.0) == "HIGH"


def test_reason_codes_generation():
    stressed_row = pd.Series({
        "NDVI": 0.22,
        "NDVI_trend": -0.025,
        "NDVI_anomaly": -1.85,
        "MNDWI": -0.15,
        "MNDWI_trend": -0.030,
        "MNDWI_anomaly": -2.10,
        "water_change": -35.0,
        "SAR_change": -1.4,
        "persistence_of_decline": 3,
        "multi_indicator_decline": 1
    })
    
    reasons = generate_reason_codes(stressed_row)
    assert len(reasons) >= 3
    assert any("NDVI trend" in r for r in reasons)
    assert any("MNDWI trend" in r for r in reasons)
    assert any("water spread" in r.lower() or "contracted" in r.lower() for r in reasons)
