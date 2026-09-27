"""
src/labels.py
Retrospective weak-supervision labeling for wetland degradation risk screening.
"""
import numpy as np
import pandas as pd


def create_retrospective_weak_labels(df):
    """
    Creates binary target 'risk_event_label' (0 or 1).
    Based on persistent multi-indicator deterioration rules.
    """
    condition_1 = (df["multi_indicator_decline"] == 1) & (df["persistence_of_decline"] >= 2)
    condition_2 = (df["MNDWI_anomaly"] < -1.2) & (df["NDVI_anomaly"] < -1.0)
    condition_3 = (df["water_change"] < -25.0) & (df["SAR_change"] < -1.0)
    
    is_concerning = condition_1 | condition_2 | condition_3
    
    df = df.copy()
    df["risk_event_label"] = is_concerning.astype(int)
    return df


def get_label_rationale_docs():
    """Returns formal documentation of weak labeling rules."""
    return {
        "label_name": "risk_event_label",
        "type": "Retrospective Weak-Supervision Heuristic",
        "positive_class": "Concerning deterioration pattern detected (1)",
        "negative_class": "Stable or normal seasonal fluctuation (0)",
        "criteria": [
            "Condition 1: Multi-indicator decline persisting across >= 2 consecutive time periods.",
            "Condition 2: Concurrently severe standardized anomalies in MNDWI (<-1.2 sigma) and NDVI (<-1.0 sigma).",
            "Condition 3: Water extent decline > 25% accompanied by SAR backscatter loss (> 1.0 dB reduction)."
        ],
        "scientific_disclaimer": (
            "These labels serve strictly as decision-support screening targets. "
            "They reflect statistical and multi-sensor deviations from baseline, not legal adjudication."
        )
    }
