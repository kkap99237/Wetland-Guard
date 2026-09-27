"""
src/indicators.py
Vectorized spectral index computations and physical validity checks
for Sentinel-2 optical data.
"""
import numpy as np
import pandas as pd


def compute_ndvi(nir, red):
    """
    Normalized Difference Vegetation Index (NDVI)
    Formula: (NIR - RED) / (NIR + RED)
    """
    nir = np.asarray(nir, dtype=np.float64)
    red = np.asarray(red, dtype=np.float64)
    denom = nir + red
    with np.errstate(divide="ignore", invalid="ignore"):
        res = np.where(np.abs(denom) > 1e-6, (nir - red) / denom, np.nan)
    return np.clip(res, -1.0, 1.0)


def compute_mndwi(green, swir1):
    """
    Modified Normalized Difference Water Index (MNDWI - Xu, 2006)
    Formula: (GREEN - SWIR1) / (GREEN + SWIR1)
    """
    green = np.asarray(green, dtype=np.float64)
    swir1 = np.asarray(swir1, dtype=np.float64)
    denom = green + swir1
    with np.errstate(divide="ignore", invalid="ignore"):
        res = np.where(np.abs(denom) > 1e-6, (green - swir1) / denom, np.nan)
    return np.clip(res, -1.0, 1.0)


def compute_evi(nir, red, blue):
    """
    Enhanced Vegetation Index (EVI)
    Formula: 2.5 * (NIR - RED) / (NIR + 6.0 * RED - 7.5 * BLUE + 1.0)
    """
    nir = np.asarray(nir, dtype=np.float64)
    red = np.asarray(red, dtype=np.float64)
    blue = np.asarray(blue, dtype=np.float64)
    denom = nir + 6.0 * red - 7.5 * blue + 1.0
    with np.errstate(divide="ignore", invalid="ignore"):
        res = np.where(np.abs(denom) > 1e-6, 2.5 * (nir - red) / denom, np.nan)
    return np.clip(res, -1.0, 2.5)


def compute_awei_nsh(green, swir1, nir, swir2):
    """
    Automated Water Extraction Index non-shadow (AWEI_nsh - Feyisa et al., 2014)
    Formula: 4.0 * (GREEN - SWIR1) - (0.25 * NIR + 2.75 * SWIR2)
    """
    green = np.asarray(green, dtype=np.float64)
    swir1 = np.asarray(swir1, dtype=np.float64)
    nir = np.asarray(nir, dtype=np.float64)
    swir2 = np.asarray(swir2, dtype=np.float64)
    res = 4.0 * (green - swir1) - (0.25 * nir + 2.75 * swir2)
    return np.clip(res, -5.0, 5.0)


def validate_index_ranges(df):
    """
    Validates physical validity ranges of calculated indices in a DataFrame.
    """
    checks = {
        "NDVI": (-1.0, 1.0),
        "MNDWI": (-1.0, 1.0),
        "EVI": (-1.0, 2.5),
        "AWEI": (-5.0, 5.0),
    }
    report = {}
    for col, (vmin, vmax) in checks.items():
        if col in df.columns:
            series = pd.to_numeric(df[col], errors="coerce")
            out_of_bounds = ((series < vmin) | (series > vmax)).sum()
            nan_count = series.isna().sum()
            report[col] = {
                "valid_range": (vmin, vmax),
                "out_of_bounds_count": int(out_of_bounds),
                "nan_count": int(nan_count),
                "min_observed": float(series.min()) if not series.empty and not pd.isna(series.min()) else None,
                "max_observed": float(series.max()) if not series.empty and not pd.isna(series.max()) else None,
            }
    return report
