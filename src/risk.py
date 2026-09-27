"""
src/risk.py
Risk scoring, communication thresholds, and multi-criteria priority ranking
for wetland field investigation screening.
"""
import numpy as np
import pandas as pd


def compute_risk_score(probability):
    """
    Converts ML probability (0.0 to 1.0) into communication risk score (0 to 100).
    """
    prob = np.asarray(probability, dtype=np.float64)
    return np.round(np.clip(prob * 100.0, 0.0, 100.0), 1)


def categorize_risk(score):
    """
    Assigns communication risk category:
    0 - 34: LOW
    35 - 69: MEDIUM
    70 - 100: HIGH
    """
    if pd.isna(score):
        return "UNKNOWN"
    if score >= 70.0:
        return "HIGH"
    elif score >= 35.0:
        return "MEDIUM"
    else:
        return "LOW"


def rank_wetlands_prioritization(latest_df):
    """
    Ranks wetlands from highest risk to lowest risk for field inspection.
    """
    df = latest_df.copy()
    if "risk_score" not in df.columns:
        raise ValueError("DataFrame must contain risk_score.")
        
    df["risk_category"] = df["risk_score"].apply(categorize_risk)
    df = df.sort_values("risk_score", ascending=False).reset_index(drop=True)
    df["priority_rank"] = np.arange(1, len(df) + 1)
    return df
