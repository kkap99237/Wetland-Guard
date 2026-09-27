"""
src/explanations.py
Evidence-based reason codes and model explainability.
Generates 3-5 specific, quantitative justification statements
for each wetland's degradation risk score.
"""
import numpy as np
import pandas as pd


def generate_reason_codes(row):
    """
    Generates 3 to 5 evidence-based reason codes grounded in measured features.
    """
    reasons = []
    
    # 1. NDVI Trend & Anomaly
    ndvi_trend = row.get("NDVI_trend", 0.0)
    ndvi_anomaly = row.get("NDVI_anomaly", 0.0)
    ndvi_val = row.get("NDVI", 0.0)
    if ndvi_trend < -0.015:
        reasons.append(f"Persistent vegetation vigor decline (NDVI trend: {ndvi_trend:.3f}/period)")
    elif ndvi_anomaly < -1.0:
        reasons.append(f"Vegetation vigor is {abs(ndvi_anomaly):.1f} standard deviations below historical baseline (NDVI: {ndvi_val:.2f})")
        
    # 2. MNDWI & Water Signal
    mndwi_trend = row.get("MNDWI_trend", 0.0)
    mndwi_anomaly = row.get("MNDWI_anomaly", 0.0)
    mndwi_val = row.get("MNDWI", 0.0)
    if mndwi_trend < -0.015:
        reasons.append(f"Open water signal contracting rapidly (MNDWI trend: {mndwi_trend:.3f}/period)")
    elif mndwi_anomaly < -1.0:
        reasons.append(f"Surface water is {abs(mndwi_anomaly):.1f} standard deviations below seasonal expectations (MNDWI: {mndwi_val:.2f})")
        
    # 3. Water Change
    water_change = row.get("water_change", 0.0)
    if water_change < -15.0:
        reasons.append(f"Historical water spread contracted by {abs(water_change):.1f}% relative to reference baseline")
        
    # 4. SAR Change & Radar Anomaly
    sar_change = row.get("SAR_change", 0.0)
    sar_anomaly = row.get("SAR_anomaly", 0.0)
    if sar_change < -0.8:
        reasons.append(f"SAR radar backscatter dropped by {abs(sar_change):.1f} dB (indicating surface moisture loss)")
    elif sar_anomaly < -1.0:
        reasons.append(f"Sentinel-1 radar wetness anomaly detected ({sar_anomaly:.1f} standard deviations from mean)")
        
    # 5. Multi-indicator / Persistence
    persist = row.get("persistence_of_decline", 0)
    multi = row.get("multi_indicator_decline", 0)
    if multi == 1 and persist >= 2:
        reasons.append(f"Sustained multi-indicator deterioration confirmed across {persist} consecutive observation cycles")
    elif persist >= 3:
        reasons.append(f"Vegetation stress prolonged over {persist} consecutive months")
        
    if len(reasons) == 0:
        reasons.append("Optical vegetation and water indices align within expected historical range")
        reasons.append("Radar backscatter indicates stable surface moisture conditions")
        reasons.append("No multi-indicator deterioration pattern observed")
        
    return reasons[:5]


def compute_feature_importances(rf_model, feature_names):
    """Extracts feature importances from trained Random Forest."""
    importances = rf_model.feature_importances_
    df_imp = pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    }).sort_values("importance", ascending=False).reset_index(drop=True)
    return df_imp
