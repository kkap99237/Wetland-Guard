"""
pages/3_Risk_Prioritization.py
Priority Ranking Table for Field Investigation Screening,
CSV Export, and External Real Satellite CSV Ingestion Interface.
"""
import streamlit as st
import pandas as pd
import numpy as np

from src.dashboard_utils import get_all_observations, get_models, compute_scores_for_date
from src.preprocessing import parse_uploaded_csv
from src.temporal_features import engineer_all_temporal_features
from src.model import prepare_features, predict_risk
from src.risk import compute_risk_score, categorize_risk, rank_wetlands_prioritization
from src.explanations import generate_reason_codes
from src.ui_theme import apply_custom_css, render_header, render_sidebar

st.set_page_config(page_title="Risk Prioritisation | Wetland Guard", page_icon="📋", layout="wide")

# Apply enterprise styling
apply_custom_css()
render_sidebar()

# Page Executive Header
render_header(
    title="Field Investigation Risk Prioritisation",
    subtitle="Decision-Support Triage Engine to Prioritise Field Inspections, Ground Patrols, and Conservation Interventions",
    tag="Triage & Field Dispatch"
)

df_all = get_all_observations()
rf_data, _, _ = get_models()

if df_all is None or rf_data is None:
    st.error("Model artifacts or observation features missing. Run train_model.py first.")
    st.stop()

# Date selection for ranking
all_dates = sorted(df_all["date"].dt.strftime("%Y-%m-%d").unique())

col_t1, col_t2 = st.columns([3, 2])
with col_t1:
    selected_date = st.selectbox(
        "Select Satellite Observation Period for Prioritisation:",
        all_dates,
        index=len(all_dates) - 1,
        help="Select any monthly composite to inspect the ranked triage priority for that month."
    )
with col_t2:
    st.markdown(f"""
    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; margin-top: 24px; display: flex; align-items: center; justify-content: space-between;">
        <span style="font-size: 0.78rem; font-weight: 600; color: #64748b;">EVALUATION CYCLE</span>
        <span style="font-size: 0.95rem; font-weight: 700; color: #065f46;">📅 {selected_date}</span>
    </div>
    """, unsafe_allow_html=True)

scores_df = compute_scores_for_date(df_all, selected_date)

# Summary Status Badges
n_high = (scores_df["risk_category"] == "HIGH").sum()
n_med = (scores_df["risk_category"] == "MEDIUM").sum()
n_low = (scores_df["risk_category"] == "LOW").sum()

s1, s2, s3 = st.columns(3)
with s1:
    st.markdown(f"""
    <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px; padding: 12px; display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 1.5rem;">🚨</span>
        <div>
            <div style="font-size: 0.75rem; font-weight: 700; color: #991b1b; text-transform: uppercase;">High Priority ({n_high} Sites)</div>
            <div style="font-size: 0.8rem; color: #7f1d1d;">Dispatch immediate ground inspection team</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with s2:
    st.markdown(f"""
    <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px; padding: 12px; display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 1.5rem;">⚠️</span>
        <div>
            <div style="font-size: 0.75rem; font-weight: 700; color: #92400e; text-transform: uppercase;">Medium Priority ({n_med} Sites)</div>
            <div style="font-size: 0.8rem; color: #78350f;">Assign to secondary satellite watchlist</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with s3:
    st.markdown(f"""
    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 12px; display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 1.5rem;">🌿</span>
        <div>
            <div style="font-size: 0.75rem; font-weight: 700; color: #166534; text-transform: uppercase;">Low Priority ({n_low} Sites)</div>
            <div style="font-size: 0.8rem; color: #14532d;">Normal seasonal baseline status</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Filters Row
st.markdown("""
<div class="wg-section-title">
    <span>🔍</span> Multi-Criteria Filtering & Search
</div>
""", unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
with col_f1:
    category_filter = st.multiselect(
        "Filter by Risk Category:",
        options=["HIGH", "MEDIUM", "LOW"],
        default=["HIGH", "MEDIUM", "LOW"]
    )
with col_f2:
    search_query = st.text_input("Search Wetland Name or ID:", "")
with col_f3:
    sort_by = st.selectbox(
        "Sort Table By:",
        ["priority_rank", "risk_score", "area", "data_quality"],
        index=0,
        format_func=lambda x: {
            "priority_rank": "Priority Rank (#1 First)",
            "risk_score": "Risk Score (Highest First)",
            "area": "Surface Area (Largest First)",
            "data_quality": "Data Quality Score"
        }.get(x, x)
    )

filtered_df = scores_df[scores_df["risk_category"].isin(category_filter)].copy()
if search_query.strip():
    q = search_query.strip().lower()
    filtered_df = filtered_df[
        filtered_df["wetland_name"].str.lower().str.contains(q) |
        filtered_df["wetland_id"].str.lower().str.contains(q)
    ]

ascending = True if sort_by in ["priority_rank"] else False
filtered_df = filtered_df.sort_values(sort_by, ascending=ascending)

# Display table
st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; margin-bottom: 8px;">
    <div style="font-size: 1rem; font-weight: 700; color: #0f172a;">
        Prioritised Wetland Inspection List ({len(filtered_df)} of {len(scores_df)} sites matching)
    </div>
</div>
""", unsafe_allow_html=True)

display_cols = [
    "priority_rank", "wetland_name", "risk_score", "risk_category",
    "NDVI", "NDVI_trend", "MNDWI", "MNDWI_trend",
    "water_change", "SAR_change", "data_quality", "top_reason"
]
table_df = filtered_df[display_cols].copy()
table_df.columns = [
    "Rank", "Wetland Name", "Risk Score", "Category",
    "NDVI", "NDVI Trend", "MNDWI", "MNDWI Trend",
    "Water Spread Δ (%)", "SAR Δ (dB)", "Data Quality", "Primary Reason"
]

def highlight_category(val):
    if val == "HIGH":
        return "background-color: #fee2e2; color: #991b1b; font-weight: bold;"
    elif val == "MEDIUM":
        return "background-color: #fef3c7; color: #92400e; font-weight: bold;"
    elif val == "LOW":
        return "background-color: #dcfce7; color: #166534; font-weight: bold;"
    return ""

st.dataframe(
    table_df.style.map(highlight_category, subset=["Category"])
    .format({
        "Risk Score": "{:.1f}",
        "NDVI": "{:.2f}",
        "NDVI Trend": "{:+.3f}",
        "MNDWI": "{:.2f}",
        "MNDWI Trend": "{:+.3f}",
        "Water Spread Δ (%)": "{:+.1f}%",
        "SAR Δ (dB)": "{:+.2f}",
        "Data Quality": "{:.0%}"
    }),
    use_container_width=True,
    height=460
)

# Export and Action Row
col_exp1, col_exp2 = st.columns([3, 2])
with col_exp1:
    csv_bytes = table_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Prioritisation Table (CSV)",
        data=csv_bytes,
        file_name=f"wetland_guard_prioritization_{selected_date}.csv",
        mime="text/csv",
        help="Export prioritized inspection table for field staff and GIS integration."
    )

st.markdown("---")

# CSV Ingestion Section
st.markdown("""
<div class="wg-section-title">
    <span>📤</span> Ingest External Real Satellite Observation CSV
</div>
<div class="wg-section-subtitle">
    Upload external satellite time-series composites (e.g., exported from Google Earth Engine or local GIS pipelines).
    The system validates physical index boundaries, computes backward-looking temporal lag features, and executes ML inference.
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose CSV File to Ingest",
    type=["csv"],
    help="CSV must contain: wetland_id, date, NDVI, MNDWI, SAR_VV, water_change."
)

if uploaded_file is not None:
    try:
        custom_df = parse_uploaded_csv(uploaded_file)
        st.success(f"✅ Successfully parsed and verified {len(custom_df)} external observations!")
        
        with st.spinner("⚡ Engineering strictly backward-looking temporal features & running Random Forest inference..."):
            custom_feat = engineer_all_temporal_features(custom_df)
            
            # Predict
            model = rf_data["model"]
            imputer = rf_data["imputer"]
            X_cust, _ = prepare_features(custom_feat)
            probs = predict_risk(model, imputer, X_cust)
            custom_feat["risk_score"] = compute_risk_score(probs)
            custom_feat["risk_category"] = custom_feat["risk_score"].apply(categorize_risk)
            
            reasons = []
            for _, r in custom_feat.iterrows():
                rc = generate_reason_codes(r)
                reasons.append(rc[0] if rc else "Normal baseline")
            custom_feat["top_reason"] = reasons
            
            st.markdown("#### External Satellite Ingestion Results:")
            st.dataframe(
                custom_feat[["wetland_id", "date", "NDVI", "MNDWI", "risk_score", "risk_category", "top_reason"]].head(25),
                use_container_width=True
            )
    except Exception as e:
        st.error(f"❌ Error processing uploaded CSV: {str(e)}")
