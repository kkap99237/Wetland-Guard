"""
src/gee_data.py
Google Earth Engine (GEE) integration for Sentinel-2, Sentinel-1,
and JRC Global Surface Water extraction using server-side reducers.
Includes graceful fallback and authentication diagnostics.
"""
import os
import json
import numpy as np
import pandas as pd

try:
    import ee
    EE_INSTALLED = True
except ImportError:
    EE_INSTALLED = False


def init_earth_engine(project_id=None):
    """
    Initializes Earth Engine safely.
    Returns (success: bool, message: str)
    """
    if not EE_INSTALLED:
        return False, "earthengine-api is not installed."
    try:
        if project_id:
            ee.Initialize(project=project_id)
        else:
            ee.Initialize()
        return True, "Google Earth Engine successfully initialized."
    except Exception as e:
        msg = (
            f"Google Earth Engine authentication required or project initialization failed: {str(e)}\n"
            "To authenticate locally, run:\n"
            "  earthengine authenticate\n"
            "  ee.Initialize(project='your-gcp-project-id')\n"
            "Wetland Guard is continuing seamlessly with the Real Satellite Ingestion pipeline."
        )
        return False, msg


def mask_s2_clouds(image):
    """
    Masks clouds and cirrus in Sentinel-2 Harmonized using QA60 bitmask.
    Bit 10: Opaque clouds, Bit 11: Cirrus
    """
    qa = image.select("QA60")
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
        qa.bitwiseAnd(cirrus_bit_mask).eq(0)
    )
    return image.updateMask(mask).divide(10000.0)


def extract_sentinel2_indices(image):
    """
    Calculates NDVI, MNDWI, EVI, and AWEI on a Sentinel-2 image.
    Bands: B2=Blue, B3=Green, B4=Red, B8=NIR, B11=SWIR1, B12=SWIR2
    """
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    mndwi = image.normalizedDifference(["B3", "B11"]).rename("MNDWI")
    evi = image.expression(
        "2.5 * ((NIR - RED) / (NIR + 6.0 * RED - 7.5 * BLUE + 1.0))",
        {
            "NIR": image.select("B8"),
            "RED": image.select("B4"),
            "BLUE": image.select("B2")
        }
    ).rename("EVI")
    awei = image.expression(
        "4.0 * (GREEN - SWIR1) - (0.25 * NIR + 2.75 * SWIR2)",
        {
            "GREEN": image.select("B3"),
            "SWIR1": image.select("B11"),
            "NIR": image.select("B8"),
            "SWIR2": image.select("B12")
        }
    ).rename("AWEI")
    return image.addBands([ndvi, mndwi, evi, awei])
