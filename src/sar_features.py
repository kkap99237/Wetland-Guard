"""
src/sar_features.py
Sentinel-1 C-band synthetic aperture radar (SAR) feature extraction,
cross-polarization ratio, and radar anomaly computation.
"""
import numpy as np
import pandas as pd


def compute_sar_cross_ratio(vh_db, vv_db):
    """
    Cross-polarization ratio (VH - VV in dB).
    Higher values typically correspond to volume scattering from emergent vegetation canopy.
    """
    vh = np.asarray(vh_db, dtype=np.float64)
    vv = np.asarray(vv_db, dtype=np.float64)
    return vh - vv


def compute_sar_change(series, periods=1):
    """
    First difference of SAR backscatter: SAR(t) - SAR(t - periods).
    """
    s = pd.Series(series)
    return s.diff(periods=periods)


def compute_sar_anomaly(series, baseline_mean, baseline_std):
    """
    Standardized radar backscatter anomaly relative to historical baseline.
    """
    s = pd.to_numeric(pd.Series(series), errors="coerce")
    std = baseline_std if baseline_std > 1e-4 else 1.0
    return (s - baseline_mean) / std


def document_sar_limitations():
    """Returns scientific caveats and limitations of Sentinel-1 SAR in wetland monitoring."""
    return (
        "Sentinel-1 SAR Caveats:\n"
        "1. Auxiliary Indicator: SAR is sensitive to dielectric constant (water content) "
        "and surface roughness, but specular reflection from open calm water causes low backscatter (-20 to -15 dB).\n"
        "2. Vegetation Structure: Dense emergent reeds or flooded vegetation can cause double-bounce reflection, "
        "increasing backscatter rather than lowering it.\n"
        "3. Acquisition Geometry: Orbit direction (Ascending vs Descending) and incidence angle affect return values.\n"
        "4. SAR change must be interpreted jointly with optical indices (MNDWI/NDVI) rather than in isolation."
    )
