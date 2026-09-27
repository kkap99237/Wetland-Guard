"""
src/water_history.py
Historical surface water dynamics, water occurrence, recurrence,
and persistent change metrics (inspired by JRC Global Surface Water).
"""
import numpy as np
import pandas as pd


def compute_water_occurrence(mndwi_series, threshold=0.0):
    """
    Computes percentage of valid observations classified as open water (MNDWI > threshold).
    """
    s = pd.Series(mndwi_series).dropna()
    if len(s) == 0:
        return 0.0
    water_count = (s > threshold).sum()
    return float(water_count / len(s) * 100.0)


def compute_water_recurrence(water_flags_series):
    """
    Calculates recurrence (how frequently water returned in successive annual/seasonal cycles).
    """
    s = pd.Series(water_flags_series).dropna()
    if len(s) < 2:
        return 1.0
    transitions = (s != s.shift(1)).sum()
    stability = 1.0 - (transitions / len(s))
    return float(np.clip(stability, 0.0, 1.0))


def compute_water_change(current_extent, baseline_extent):
    """
    Computes relative change in water occurrence or surface water extent.
    Negative values indicate water loss.
    """
    if pd.isna(current_extent) or pd.isna(baseline_extent):
        return 0.0
    if baseline_extent <= 1e-4:
        return 0.0
    return float((current_extent - baseline_extent) / baseline_extent * 100.0)
