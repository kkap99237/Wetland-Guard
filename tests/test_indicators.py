"""
tests/test_indicators.py
Unit tests for spectral indicator calculations and boundary conditions.
"""
import numpy as np
import pandas as pd
import pytest
from src.indicators import compute_ndvi, compute_mndwi, compute_evi, compute_awei_nsh, validate_index_ranges


def test_compute_ndvi_bounds():
    nir = [0.8, 0.4, 0.1]
    red = [0.2, 0.4, 0.6]
    ndvi = compute_ndvi(nir, red)
    assert np.all(ndvi >= -1.0)
    assert np.all(ndvi <= 1.0)
    assert pytest.approx(ndvi[0], 0.01) == 0.60
    assert pytest.approx(ndvi[1], 0.01) == 0.00
    assert pytest.approx(ndvi[2], 0.01) == -0.714


def test_compute_ndvi_zero_division():
    nir = [0.0, 0.0]
    red = [0.0, 0.0]
    ndvi = compute_ndvi(nir, red)
    assert np.all(np.isnan(ndvi))


def test_compute_mndwi_bounds():
    green = [0.5, 0.1, 0.2]
    swir1 = [0.1, 0.5, 0.2]
    mndwi = compute_mndwi(green, swir1)
    assert np.all(mndwi >= -1.0)
    assert np.all(mndwi <= 1.0)
    assert pytest.approx(mndwi[0], 0.01) == 0.667
    assert pytest.approx(mndwi[1], 0.01) == -0.667
    assert pytest.approx(mndwi[2], 0.01) == 0.000


def test_compute_evi_bounds():
    nir = [0.7, 0.3]
    red = [0.1, 0.3]
    blue = [0.05, 0.15]
    evi = compute_evi(nir, red, blue)
    assert np.all(evi >= -1.0)
    assert np.all(evi <= 2.5)


def test_compute_awei_nsh():
    green = [0.4, 0.1]
    swir1 = [0.1, 0.3]
    nir = [0.2, 0.1]
    swir2 = [0.05, 0.2]
    awei = compute_awei_nsh(green, swir1, nir, swir2)
    assert len(awei) == 2
    assert awei[0] > 0


def test_validate_index_ranges():
    df = pd.DataFrame({
        "NDVI": [0.5, -0.2, 1.5],
        "MNDWI": [0.3, -0.1, 0.2]
    })
    report = validate_index_ranges(df)
    assert "NDVI" in report
    assert report["NDVI"]["out_of_bounds_count"] == 1
    assert report["MNDWI"]["out_of_bounds_count"] == 0
