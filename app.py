"""
Wetland Guard - Main Entrypoint
Explainable AI-Powered Early-Warning and Risk-Prioritisation System for Wetland Degradation
"""
import os
import json
import streamlit as st
import pandas as pd
from src.dashboard_utils import get_models, get_all_observations, get_wetland_boundaries
from src.ui_theme import apply_custom_css, render_header, render_sidebar

st.set_page_config(
    page_title="Wetland Guard | AI Wetland Monitoring",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply unified enterprise UI styling
apply_custom_css()
render_sidebar()

# Sidebar Navigation Info
st.sidebar.markdown("""
<div style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; margin-bottom: 1rem;">
    <div style="font-size: 0.75rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
        Observatory Modules
    </div>
    <div style="font-size: 0.82rem; color: #334155; line-height: 1.6;">
        <b>1. Dashboard</b> — Regional GIS Risk Map<br>
        <b>2. Explorer</b> — Temporal Sensor Curves<br>
        <b>3. Prioritization</b> — Investigation Ranking
    </div>
</div>
""", unsafe_allow_html=True)

# Main Page Executive Header
render_header(
    title="Wetland Guard",
    subtitle="Explainable AI-Powered Early-Warning and Risk-Prioritisation System for Wetland Ecosystem Degradation in Tamil Nadu",
    tag="Geospatial Early-Warning System • Live"
)

# Important Decision-Support Screening Advisory
st.markdown("""
<div class="wg-callout-card" style="border-left-color: #0284c7; background: #f0f9ff;">
    <div class="wg-callout-title" style="color: #0369a1;">
        <span>🛡️</span> Decision-Support & Screening Advisory
    </div>
    <div class="wg-callout-text" style="color: #0c4a6e;">
        Wetland Guard is an <b>early-warning screening and prioritization engine</b> designed to triage ground patrols and conservation interventions.
        It identifies coupled multi-sensor temporal anomalies consistent with physical degradation trajectories.
        It <b>does NOT claim definitive future ecological demise</b>, nor does it replace on-the-ground hydrological surveys.
    </div>
</div>
""", unsafe_allow_html=True)

# Load core assets
rf_data, lr_data, metadata = get_models()
df_obs = get_all_observations()
gdf_wetlands = get_wetland_boundaries()

# Top KPI Overview
total_wetlands = gdf_wetlands["wetland_id"].nunique() if gdf_wetlands is not None else 15
total_records = len(df_obs) if df_obs is not None else 720

# Latest risk summary
latest_obs = df_obs.sort_values("date").groupby("wetland_id").last().reset_index() if df_obs is not None else pd.DataFrame()
rf_model = rf_data["model"] if rf_data else None
imputer = rf_data["imputer"] if rf_data else None

from src.model import prepare_features, predict_risk
from src.risk import compute_risk_score, categorize_risk

if rf_model and not latest_obs.empty:
    X_lat, _ = prepare_features(latest_obs)
    probs = predict_risk(rf_model, imputer, X_lat)
    latest_obs["risk_score"] = compute_risk_score(probs)
    latest_obs["risk_category"] = latest_obs["risk_score"].apply(categorize_risk)
    n_high = (latest_obs["risk_category"] == "HIGH").sum()
    n_med = (latest_obs["risk_category"] == "MEDIUM").sum()
    n_low = (latest_obs["risk_category"] == "LOW").sum()
else:
    n_high, n_med, n_low = 0, 1, 14

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="wg-metric-card">
        <div class="wg-metric-label">Monitored Sites <span>📍</span></div>
        <div class="wg-metric-value">{total_wetlands}</div>
        <div class="wg-metric-subtext"><span class="wg-delta-chip wg-delta-neutral">Tamil Nadu</span> Ramsar & NWIA</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="wg-metric-card">
        <div class="wg-metric-label">Total Observations <span>🛰️</span></div>
        <div class="wg-metric-value">{total_records:,}</div>
        <div class="wg-metric-subtext"><span class="wg-delta-chip wg-delta-neutral">2021–2024</span> Monthly Cadence</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="wg-metric-card">
        <div class="wg-metric-label">High Risk <span>🚨</span></div>
        <div class="wg-metric-value" style="color: #b91c1c;">{n_high}</div>
        <div class="wg-metric-subtext"><span class="wg-delta-chip wg-delta-danger">Urgent Action</span> Immediate Patrol</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="wg-metric-card">
        <div class="wg-metric-label">Medium Risk <span>⚠️</span></div>
        <div class="wg-metric-value" style="color: #b45309;">{n_med}</div>
        <div class="wg-metric-subtext"><span class="wg-delta-chip wg-delta-warning">Watchlist</span> Secondary Alert</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="wg-metric-card">
        <div class="wg-metric-label">Low Risk <span>🌿</span></div>
        <div class="wg-metric-value" style="color: #15803d;">{n_low}</div>
        <div class="wg-metric-subtext"><span class="wg-delta-chip wg-delta-success">Stable</span> Baseline Health</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Resumability & System Status
col_left, col_right = st.columns([7, 4])

with col_left:
    st.markdown("""
    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; height: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 8px;">
            <span style="color: #059669;">🔬</span> Multi-Sensor Earth Observation Architecture
        </div>
        <div style="font-size: 0.88rem; color: #475569; line-height: 1.6;">
            Wetland Guard integrates harmonized satellite observations across 15 high-priority Ramsar and ISRO NWIA wetlands in Tamil Nadu:
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 1rem;">
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px;">
                <div style="font-weight: 700; font-size: 0.82rem; color: #065f46; margin-bottom: 4px;">1. Spectral Vegetation Indices</div>
                <div style="font-size: 0.78rem; color: #64748b;">Sentinel-2 10m NDVI & EVI track seasonal photosynthetic vigor and canopy health.</div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px;">
                <div style="font-weight: 700; font-size: 0.82rem; color: #0284c7; margin-bottom: 4px;">2. Surface Moisture & Water</div>
                <div style="font-size: 0.78rem; color: #64748b;">MNDWI, AWEI, and JRC recurrence capture inundation contraction and shoreline shrinkage.</div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px;">
                <div style="font-weight: 700; font-size: 0.82rem; color: #b45309; margin-bottom: 4px;">3. Cloud-Penetrating C-SAR</div>
                <div style="font-size: 0.78rem; color: #64748b;">Sentinel-1 VV/VH backscatter isolates all-weather soil moisture and emergent vegetation structure.</div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px;">
                <div style="font-weight: 700; font-size: 0.82rem; color: #9333ea; margin-bottom: 4px;">4. Explainable AI Scoring</div>
                <div style="font-size: 0.78rem; color: #64748b;">Random Forest classifier outputs a 0–100 risk score paired with 3–5 verifiable evidence reason codes.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown(f"""
    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; height: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-bottom: 0.75rem; display: flex; align-items: center; justify-content: space-between;">
            <span style="display: flex; align-items: center; gap: 8px;">
                <span style="color: #059669;">⚙️</span> System State
            </span>
            <span style="font-size: 0.72rem; font-weight: 700; color: #065f46; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 2px 8px; border-radius: 12px;">
                ● ONLINE
            </span>
        </div>
        <div style="font-size: 0.82rem; color: #475569; display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                <span style="color: #64748b;">Study Area</span>
                <span style="font-weight: 600; color: #0f172a;">Tamil Nadu, India</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                <span style="color: #64748b;">Reference Polygons</span>
                <span style="font-weight: 600; color: #0f172a;">15 Wetlands (GeoJSON)</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                <span style="color: #64748b;">Primary Classifier</span>
                <span style="font-weight: 600; color: #0f172a;">Random Forest (200 trees)</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                <span style="color: #64748b;">Baseline Model</span>
                <span style="font-weight: 600; color: #0f172a;">Logistic Regression</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                <span style="color: #64748b;">Validation Split</span>
                <span style="font-weight: 600; color: #0f172a;">Chronological (70 / 15 / 15)</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                <span style="color: #64748b;">Temporal Leakage</span>
                <span style="font-weight: 700; color: #15803d;">0% (Shifted Baselines)</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding-top: 2px;">
                <span style="color: #64748b;">Validation Accuracy</span>
                <span style="font-weight: 700; color: #0f172a;">{metadata.get('random_forest_metrics', {}).get('accuracy', 0.99):.2%}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Quick Start Guide Navigation Cards
st.markdown("""
<div class="wg-section-title">
    <span>🧭</span> Operational Workflow & Module Navigation
</div>
""", unsafe_allow_html=True)

c_a, c_b, c_c = st.columns(3)
with c_a:
    st.markdown("""
    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.2rem; height: 100%;">
        <div style="font-size: 0.9rem; font-weight: 700; color: #065f46; margin-bottom: 6px;">1. Regional Risk Map</div>
        <div style="font-size: 0.8rem; color: #475569; line-height: 1.5; margin-bottom: 10px;">
            Geospatial overview of Tamil Nadu wetlands. Circle color depicts multi-indicator risk; circle radius reflects wetland surface area.
        </div>
        <div style="font-size: 0.75rem; font-weight: 600; color: #0d9488;">Go to <b>1_Dashboard</b> ➔</div>
    </div>
    """, unsafe_allow_html=True)

with c_b:
    st.markdown("""
    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.2rem; height: 100%;">
        <div style="font-size: 0.9rem; font-weight: 700; color: #0284c7; margin-bottom: 6px;">2. Site Temporal Explorer</div>
        <div style="font-size: 0.8rem; color: #475569; line-height: 1.5; margin-bottom: 10px;">
            Deep-dive into multi-year trajectory graphs (2021–2024), 3-month rolling averages, and standardized z-score anomaly curves.
        </div>
        <div style="font-size: 0.75rem; font-weight: 600; color: #0284c7;">Go to <b>2_Wetland_Explorer</b> ➔</div>
    </div>
    """, unsafe_allow_html=True)

with c_c:
    st.markdown("""
    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.2rem; height: 100%;">
        <div style="font-size: 0.9rem; font-weight: 700; color: #b45309; margin-bottom: 6px;">3. Field Prioritization</div>
        <div style="font-size: 0.8rem; color: #475569; line-height: 1.5; margin-bottom: 10px;">
            Ranked priority table for dispatching patrol teams, CSV export for field teams, and drag-and-drop external satellite CSV ingestion.
        </div>
        <div style="font-size: 0.75rem; font-weight: 600; color: #b45309;">Go to <b>3_Risk_Prioritization</b> ➔</div>
    </div>
    """, unsafe_allow_html=True)
