"""
src/preprocessing.py
Data loading, schema validation, data quality scoring,
and external CSV ingestion for Wetland Guard.
"""
import os
import numpy as np
import pandas as pd
import geopandas as gpd


EXPECTED_COLUMNS = [
    "wetland_id", "wetland_name", "date", "latitude", "longitude",
    "area", "NDVI", "MNDWI", "EVI", "AWEI", "SAR_VV", "SAR_VH",
    "SAR_change", "water_change", "soil_moisture"
]


def load_wetland_boundaries(path="data/raw/tamil_nadu_wetlands.geojson"):
    """Loads and validates wetland boundary GeoJSON."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Wetland boundary file not found at: {path}")
    gdf = gpd.read_file(path)
    required_cols = ["wetland_id", "wetland_name", "district", "geometry"]
    for col in required_cols:
        if col not in gdf.columns:
            raise ValueError(f"Missing required column in boundary file: {col}")
    return gdf


def load_observations(path="data/processed/wetland_observations.csv"):
    """Loads real satellite observations CSV."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Observation file not found at: {path}")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df


def compute_data_quality_score(df):
    """
    Calculates a data_quality_score (0.0 to 1.0) for each observation or wetland.
    Penalizes missing values and extreme anomalies.
    """
    scores = np.ones(len(df), dtype=np.float64)
    
    if "NDVI" in df.columns:
        scores -= np.where(df["NDVI"].isna() | (df["NDVI"] < -1.0) | (df["NDVI"] > 1.0), 0.25, 0.0)
    if "MNDWI" in df.columns:
        scores -= np.where(df["MNDWI"].isna() | (df["MNDWI"] < -1.0) | (df["MNDWI"] > 1.0), 0.25, 0.0)
    if "EVI" in df.columns:
        scores -= np.where(df["EVI"].isna(), 0.10, 0.0)
    if "SAR_VV" in df.columns:
        scores -= np.where(df["SAR_VV"].isna(), 0.15, 0.0)
    if "water_change" in df.columns:
        scores -= np.where(df["water_change"].isna(), 0.15, 0.0)
    if "soil_moisture" in df.columns:
        scores -= np.where(df["soil_moisture"].isna(), 0.10, 0.0)
        
    return np.clip(scores, 0.1, 1.0)


def validate_observations(df):
    """
    Validates observation schema, types, and temporal continuity.
    Returns (is_valid, list_of_warnings).
    """
    warnings = []
    if "wetland_id" not in df.columns:
        return False, ["Missing wetland_id column"]
    if "date" not in df.columns:
        return False, ["Missing date column"]
        
    n_wetlands = df["wetland_id"].nunique()
    if n_wetlands < 1:
        warnings.append("Dataset contains 0 wetlands.")
        
    for wet_id, group in df.groupby("wetland_id"):
        if len(group) < 6:
            warnings.append(f"Wetland {wet_id} has fewer than 6 temporal observations ({len(group)}).")
            
    return True, warnings


def parse_uploaded_csv(file_buffer):
    """
    Safely parses an uploaded CSV file from Streamlit UI.
    Validates available columns, parses dates, and computes data quality.
    """
    df = pd.read_csv(file_buffer)
    df.columns = [c.strip() for c in df.columns]
    
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        raise ValueError("Uploaded CSV must contain a 'date' column.")
        
    if "wetland_id" not in df.columns:
        if "wetland_name" in df.columns:
            df["wetland_id"] = df["wetland_name"].astype(str)
        else:
            df["wetland_id"] = "UPLOADED_WET_01"
            
    df["data_quality"] = compute_data_quality_score(df)
    return df
