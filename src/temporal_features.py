"""
src/temporal_features.py
Temporal feature engineering for wetland time-series monitoring.
Calculates backward-looking rolling statistics, first differences,
trend slopes, and multi-indicator decline flags.

STRICT RULE: All features are calculated per wetland chronologically.
Zero future leakage is permitted.
"""
import numpy as np
import pandas as pd


def compute_linear_trend_slope(series_values):
    """
    Computes slope of linear regression for a backward-looking slice.
    y = mx + c, returns m.
    """
    y = np.asarray(series_values, dtype=np.float64)
    n = len(y)
    if n < 2 or np.isnan(y).any():
        return 0.0
    x = np.arange(n, dtype=np.float64)
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    denom = np.sum((x - x_mean) ** 2)
    if denom < 1e-6:
        return 0.0
    slope = np.sum((x - x_mean) * (y - y_mean)) / denom
    return float(slope)


def compute_temporal_features_for_group(group_df):
    """
    Computes strictly backward-looking temporal features for a single wetland group.
    Group must be sorted by date ascending before calling.
    """
    df = group_df.copy().sort_values("date").reset_index(drop=True)
    
    signals = ["NDVI", "MNDWI", "EVI", "SAR_change", "water_change", "soil_moisture"]
    
    for sig in signals:
        if sig not in df.columns:
            df[sig] = 0.0
        
        s = df[sig].astype(np.float64)
        
        # 1. First difference
        df[f"{sig}_change"] = s.diff(1).fillna(0.0)
        
        # 2. Percentage change
        prev = s.shift(1)
        with np.errstate(divide="ignore", invalid="ignore"):
            pct = np.where(np.abs(prev) > 1e-4, (s - prev) / np.abs(prev) * 100.0, 0.0)
        df[f"{sig}_pct_change"] = pd.Series(pct).fillna(0.0)
        
        # 3. Backward rolling means
        df[f"{sig}_rolling_3"] = s.rolling(window=3, min_periods=1).mean()
        df[f"{sig}_rolling_6"] = s.rolling(window=6, min_periods=1).mean()
        
        # 4. Backward 3-period trend slope
        trends = []
        for i in range(len(s)):
            if i < 2:
                trends.append(0.0)
            else:
                window_vals = s.iloc[i-2:i+1].values
                trends.append(compute_linear_trend_slope(window_vals))
        df[f"{sig}_trend"] = trends
        
        # 5. Expanding baseline mean & std up to t-1 to prevent leakage
        expanding_mean = s.shift(1).expanding(min_periods=3).mean()
        expanding_std = s.shift(1).expanding(min_periods=3).std().fillna(1.0)
        expanding_std = expanding_std.replace(0.0, 1.0)
        
        # Anomaly z-score
        z_score = (s - expanding_mean) / expanding_std
        df[f"{sig}_anomaly"] = z_score.fillna(0.0)

    # Persistence of decline
    decline_count = 0
    persistences = []
    for val in df["NDVI_anomaly"]:
        if val < -0.8:
            decline_count += 1
        else:
            decline_count = 0
        persistences.append(decline_count)
    df["persistence_of_decline"] = persistences

    # Multi-indicator decline flag
    multi_decline = (
        ((df["NDVI_trend"] < -0.01) | (df["NDVI_anomaly"] < -0.7)) &
        ((df["MNDWI_trend"] < -0.01) | (df["MNDWI_anomaly"] < -0.7) | (df["SAR_change"] < -0.5))
    ).astype(int)
    df["multi_indicator_decline"] = multi_decline

    return df


def engineer_all_temporal_features(df):
    """
    Engineers temporal features for all wetlands in a dataset.
    Preserves wetland isolation.
    """
    if "wetland_id" not in df.columns:
        raise ValueError("DataFrame must contain 'wetland_id' column.")
    if "date" not in df.columns:
        raise ValueError("DataFrame must contain 'date' column.")
        
    df["date"] = pd.to_datetime(df["date"])
    processed_groups = []
    for _, group in df.groupby("wetland_id"):
        processed = compute_temporal_features_for_group(group)
        processed_groups.append(processed)
        
    out_df = pd.concat(processed_groups, ignore_index=True)
    out_df = out_df.sort_values(["wetland_id", "date"]).reset_index(drop=True)
    return out_df
