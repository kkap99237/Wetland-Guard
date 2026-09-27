"""
tests/test_temporal_features.py
Tests for temporal feature engineering and strict no-leakage verification.
"""
import numpy as np
import pandas as pd
import pytest
from src.temporal_features import compute_linear_trend_slope, compute_temporal_features_for_group, engineer_all_temporal_features


def test_linear_trend_slope_direction():
    # Increasing series
    inc = [0.1, 0.2, 0.3]
    assert compute_linear_trend_slope(inc) > 0.0
    
    # Decreasing series
    dec = [0.5, 0.3, 0.1]
    assert compute_linear_trend_slope(dec) < 0.0
    
    # Flat series
    flat = [0.4, 0.4, 0.4]
    assert pytest.approx(compute_linear_trend_slope(flat)) == 0.0


def test_no_future_leakage():
    """
    CRITICAL NO-LEAKAGE TEST:
    Modifying future observations at t >= 5 must NOT change
    any engineered features at t <= 4.
    """
    dates = pd.date_range("2021-01-01", periods=10, freq="MS")
    df1 = pd.DataFrame({
        "wetland_id": ["W1"] * 10,
        "date": dates,
        "NDVI": [0.5, 0.48, 0.45, 0.42, 0.40, 0.38, 0.35, 0.32, 0.30, 0.28],
        "MNDWI": [0.3, 0.28, 0.26, 0.24, 0.22, 0.20, 0.18, 0.16, 0.14, 0.12]
    })
    
    feat1 = compute_temporal_features_for_group(df1)
    
    # Create altered future dataset
    df2 = df1.copy()
    # Heavily corrupt future values at t >= 5
    df2.loc[5:, "NDVI"] = 0.99
    df2.loc[5:, "MNDWI"] = -0.99
    
    feat2 = compute_temporal_features_for_group(df2)
    
    # Check that for t <= 4, all features are EXACTLY identical
    for col in ["NDVI_change", "NDVI_rolling_3", "NDVI_trend", "NDVI_anomaly", "MNDWI_change", "MNDWI_trend"]:
        v1 = feat1.loc[:4, col].values
        v2 = feat2.loc[:4, col].values
        assert np.allclose(v1, v2, equal_nan=True), f"Future data leaked into past feature: {col}"


def test_wetland_isolation():
    """
    Features for wetland A must be completely independent of wetland B.
    """
    dates = pd.date_range("2021-01-01", periods=6, freq="MS")
    df_a = pd.DataFrame({
        "wetland_id": ["W_A"] * 6,
        "date": dates,
        "NDVI": [0.2, 0.22, 0.24, 0.26, 0.28, 0.30]
    })
    df_b = pd.DataFrame({
        "wetland_id": ["W_B"] * 6,
        "date": dates,
        "NDVI": [0.8, 0.75, 0.70, 0.65, 0.60, 0.55]
    })
    
    combined = pd.concat([df_a, df_b], ignore_index=True)
    res = engineer_all_temporal_features(combined)
    
    res_a = res[res["wetland_id"] == "W_A"].sort_values("date").reset_index(drop=True)
    res_b = res[res["wetland_id"] == "W_B"].sort_values("date").reset_index(drop=True)
    
    # Isolated calculation
    iso_a = compute_temporal_features_for_group(df_a)
    assert np.allclose(res_a["NDVI_rolling_3"], iso_a["NDVI_rolling_3"])
