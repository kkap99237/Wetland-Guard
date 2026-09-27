"""
src/dashboard_utils.py
Cached loaders and UI helper functions for Streamlit pages.
"""
import os
import json
import joblib
import pandas as pd
import geopandas as gpd
import streamlit as st

from src.temporal_features import engineer_all_temporal_features
from src.labels import create_retrospective_weak_labels
from src.model import prepare_features, predict_risk
from src.risk import compute_risk_score, categorize_risk, rank_wetlands_prioritization
from src.explanations import generate_reason_codes


@st.cache_data
def get_wetland_boundaries():
    path = "data/raw/tamil_nadu_wetlands.geojson"
    if os.path.exists(path):
        return gpd.read_file(path)
    return None


@st.cache_data
def get_all_observations():
    path = "data/features/wetland_features.csv"
    if not os.path.exists(path):
        raw_path = "data/processed/wetland_observations.csv"
        df = pd.read_csv(raw_path)
        df["date"] = pd.to_datetime(df["date"])
        df = engineer_all_temporal_features(df)
        df = create_retrospective_weak_labels(df)
        df.to_csv(path, index=False)
    else:
        df = pd.read_csv(path)
        df["date"] = pd.to_datetime(df["date"])
    return df


@st.cache_resource
def get_models():
    model_path = "models/wetland_model.pkl"
    lr_path = "models/logistic_baseline.pkl"
    meta_path = "models/model_metadata.json"
    
    rf_data = joblib.load(model_path) if os.path.exists(model_path) else None
    lr_data = joblib.load(lr_path) if os.path.exists(lr_path) else None
    
    metadata = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            
    return rf_data, lr_data, metadata


def compute_scores_for_date(df_all, target_date):
    """
    Computes risk scores, categories, and reason codes for all wetlands at a specified date.
    """
    rf_data, _, _ = get_models()
    if rf_data is None:
        return None
        
    model = rf_data["model"]
    imputer = rf_data["imputer"]
    
    sub = df_all[df_all["date"] == pd.to_datetime(target_date)].copy()
    if sub.empty:
        sub = df_all[df_all["date"] <= pd.to_datetime(target_date)].sort_values("date").groupby("wetland_id").last().reset_index()
        
    X, _ = prepare_features(sub)
    probs = predict_risk(model, imputer, X)
    sub["risk_prob"] = probs
    sub["risk_score"] = compute_risk_score(probs)
    sub["risk_category"] = sub["risk_score"].apply(categorize_risk)
    sub = rank_wetlands_prioritization(sub)
    
    reasons = []
    top_reasons = []
    for _, row in sub.iterrows():
        r_list = generate_reason_codes(row)
        reasons.append("; ".join(r_list))
        top_reasons.append(r_list[0] if r_list else "Normal seasonal baseline")
        
    sub["evidence_reasons"] = reasons
    sub["top_reason"] = top_reasons
    return sub
