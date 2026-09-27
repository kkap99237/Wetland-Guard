"""
tests/test_model.py
Unit tests for chronological splitting, feature isolation, and model training.
"""
import numpy as np
import pandas as pd
import pytest
from src.model import prepare_features, chronological_split, train_random_forest, evaluate_model, predict_risk


def test_chronological_split_ordering():
    dates = pd.date_range("2021-01-01", periods=100, freq="D")
    df = pd.DataFrame({
        "date": dates,
        "val": np.arange(100)
    })
    train, val, test = chronological_split(df, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
    
    assert train["date"].max() < val["date"].min()
    assert val["date"].max() < test["date"].min()
    assert len(train) == 70
    assert len(val) == 15
    assert len(test) == 15


def test_no_label_or_id_in_features():
    df = pd.DataFrame({
        "wetland_id": ["W1", "W2"],
        "wetland_name": ["Marsh A", "Lake B"],
        "date": ["2021-01-01", "2021-02-01"],
        "risk_event_label": [0, 1],
        "NDVI": [0.5, 0.4],
        "MNDWI": [0.2, 0.1],
        "NDVI_trend": [-0.01, -0.02]
    })
    X, cols = prepare_features(df)
    assert "wetland_id" not in cols
    assert "wetland_name" not in cols
    assert "risk_event_label" not in cols
    assert "date" not in cols


def test_model_train_and_predict():
    np.random.seed(42)
    n = 60
    X = pd.DataFrame({
        "NDVI": np.random.uniform(0.1, 0.8, n),
        "MNDWI": np.random.uniform(-0.2, 0.6, n),
        "NDVI_anomaly": np.random.normal(0, 1, n)
    })
    y = (X["NDVI_anomaly"] < -0.8).astype(int).values
    
    model, imputer = train_random_forest(X, y, n_estimators=10, random_state=42)
    probs = predict_risk(model, imputer, X)
    
    assert len(probs) == n
    assert np.all(probs >= 0.0)
    assert np.all(probs <= 1.0)
