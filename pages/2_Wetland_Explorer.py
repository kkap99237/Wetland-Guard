"""
pages/2_Wetland_Explorer.py
Individual Wetland Deep-Dive: Multi-Sensor Time Series, Baseline Anomalies,
and Quantitative Explainability Justifications.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.dashboard_utils import get_wetland_boundaries, get_all_observations, get_models
from src.explanations import generate_reason_codes
from src.ui_theme import apply_custom_css, render_header, render_sidebar, get_plotly_theme

st.set_page_config(page_title="Wetland Explorer | Wetland Guard", page_icon="🔍", layout="wide")

# Apply enterprise styling
apply_custom_css()
render_sidebar()

# Page Executive Header
render_header(
    title="Wetland Temporal Explorer & Explainability",
    subtitle="Detailed Multi-Sensor Trajectories, Historical Seasonal Baselines, and Verifiable Quantitative Evidence Codes",
    tag="Site Diagnostics & Sensor Curves"
)

gdf = get_wetland_boundaries()
df_all = get_all_observations()

if gdf is None or df_all is None:
    st.error("Wetland observations not found. Run train_model.py first.")
    st.stop()

# Selection Widget Bar
wetland_list = sorted(df_all["wetland_name"].unique())

col_sel1, col_sel2 = st.columns([3, 2])
with col_sel1:
    selected_name = st.selectbox(
        "Select Wetland Site to Analyze:",
        wetland_list,
        index=0,
        help="Select any of the 15 Ramsar/NWIA monitored wetlands across Tamil Nadu."
    )

df_wetland = df_all[df_all["wetland_name"] == selected_name].sort_values("date").reset_index(drop=True)
latest_obs = df_wetland.iloc[-1]

# Metadata Cards Header
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.markdown(f"""
    <div class="wg-metric-card">
        <div class="wg-metric-label">Site ID <span>🏷️</span></div>
        <div class="wg-metric-value" style="font-size: 1.5rem;">{latest_obs['wetland_id']}</div>
        <div class="wg-metric-subtext"><span class="wg-delta-chip wg-delta-neutral">Ramsar / NWIA</span> Official Code</div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""
    <div class="wg-metric-card">
        <div class="wg-metric-label">Surface Area <span>📐</span></div>
        <div class="wg-metric-value" style="font-size: 1.5rem;">{latest_obs.get('area', 0):,.1f} <span style="font-size: 0.9rem; font-weight: 600;">ha</span></div>
        <div class="wg-metric-subtext"><span class="wg-delta-chip wg-delta-neutral">Baseline Boundary</span> GIS Extent</div>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    st.markdown(f"""
    <div class="wg-metric-card">
        <div class="wg-metric-label">Coordinates <span>🌐</span></div>
        <div class="wg-metric-value" style="font-size: 1.25rem; font-family: 'JetBrains Mono', monospace;">{latest_obs['latitude']:.3f}°N, {latest_obs['longitude']:.3f}°E</div>
        <div class="wg-metric-subtext"><span class="wg-delta-chip wg-delta-neutral">WGS 84</span> Centroid</div>
    </div>
    """, unsafe_allow_html=True)

with col_m4:
    st.markdown(f"""
    <div class="wg-metric-card">
        <div class="wg-metric-label">Latest Composite <span>📅</span></div>
        <div class="wg-metric-value" style="font-size: 1.5rem;">{latest_obs['date'].strftime('%Y-%m')}</div>
        <div class="wg-metric-subtext"><span class="wg-delta-chip wg-delta-success">Active</span> Latest Observation</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Diagnostic Briefing Card: "Why is this wetland at risk?"
reasons = generate_reason_codes(latest_obs)

col_r1, col_r2 = st.columns([6, 4])
with col_r1:
    st.markdown("""
    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; height: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 8px;">
            <span style="color: #059669;">🛡️</span> Why is this Wetland at Risk? (Evidence-Based Reasons)
        </div>
        <div style="font-size: 0.82rem; color: #64748b; margin-bottom: 12px; line-height: 1.5;">
            The following evidence statements are <b>quantitatively derived</b> by benchmarking current satellite measurements against the site's own historical seasonal baseline:
        </div>
    """, unsafe_allow_html=True)
    
    for i, r in enumerate(reasons, 1):
        st.markdown(f"""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 3px solid #059669; border-radius: 6px; padding: 8px 12px; font-size: 0.82rem; color: #1e293b; margin-bottom: 6px; line-height: 1.45;">
            <b>{i}.</b> {r}
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

with col_r2:
    st.markdown("""
    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; height: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 8px;">
            <span>🛰️</span> Latest Sensor Telemetry
        </div>
    """, unsafe_allow_html=True)
    
    c_sub1, c_sub2 = st.columns(2)
    with c_sub1:
        st.metric("NDVI Vigor", f"{latest_obs['NDVI']:.2f}", f"Trend: {latest_obs.get('NDVI_trend', 0):+.3f}")
        st.metric("SAR VV", f"{latest_obs.get('SAR_VV', 0):.1f} dB", f"Δ {latest_obs.get('SAR_change', 0):+.2f} dB")
    with c_sub2:
        st.metric("MNDWI Water", f"{latest_obs['MNDWI']:.2f}", f"Trend: {latest_obs.get('MNDWI_trend', 0):+.3f}")
        st.metric("Water Spread Δ", f"{latest_obs.get('water_change', 0):+.1f}%")
        
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Multi-Sensor Trajectories
st.markdown("""
<div class="wg-section-title">
    <span>📈</span> Multi-Sensor Trajectories & Anomaly Decomposition (2021–2024)
</div>
<div class="wg-section-subtitle">
    Explore optical, hydrological, radar, and standardized anomaly curves across 48 monthly observation cycles.
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🌿 Optical Indices (NDVI / EVI)",
    "💧 Surface Water (MNDWI / Water %)",
    "📡 Radar Backscatter (Sentinel-1 SAR)",
    "⚠️ Standardized Baseline Anomalies (Z-Scores)"
])

plotly_theme = get_plotly_theme()

with tab1:
    fig_opt = go.Figure()
    fig_opt.add_trace(go.Scatter(
        x=df_wetland["date"], y=df_wetland["NDVI"],
        mode="lines+markers", name="NDVI (Measured)",
        line=dict(color="#059669", width=2.5),
        marker=dict(size=5, color="#059669")
    ))
    if "NDVI_rolling_3" in df_wetland.columns:
        fig_opt.add_trace(go.Scatter(
            x=df_wetland["date"], y=df_wetland["NDVI_rolling_3"],
            mode="lines", name="NDVI (3-Month Smoothed)",
            line=dict(color="#10b981", width=1.8, dash="dash")
        ))
    if "EVI" in df_wetland.columns:
        fig_opt.add_trace(go.Scatter(
            x=df_wetland["date"], y=df_wetland["EVI"],
            mode="lines", name="EVI (Enhanced Veg)",
            line=dict(color="#0284c7", width=1.5, dash="dot")
        ))
    fig_opt.update_layout(
        **plotly_theme,
        title=dict(text=f"Vegetation Vigor Trajectory: {selected_name}", font=dict(size=14, weight=700)),
        xaxis_title="Observation Date",
        yaxis_title="Index Value [-1.0 to 1.0]",
        height=420,
        hovermode="x unified"
    )
    st.plotly_chart(fig_opt, use_container_width=True)

with tab2:
    fig_wat = make_subplots(specs=[[{"secondary_y": True}]])
    fig_wat.add_trace(
        go.Scatter(
            x=df_wetland["date"], y=df_wetland["MNDWI"],
            mode="lines+markers", name="MNDWI (Water Index)",
            line=dict(color="#0284c7", width=2.5),
            marker=dict(size=5, color="#0284c7")
        ),
        secondary_y=False
    )
    # Threshold line at MNDWI = 0 (open water)
    fig_wat.add_hline(
        y=0.0, line_dash="dash", line_color="rgba(15, 23, 42, 0.4)",
        annotation_text="Open Water Threshold (MNDWI = 0.0)",
        annotation_position="bottom right"
    )
    
    if "water_change" in df_wetland.columns:
        fig_wat.add_trace(
            go.Bar(
                x=df_wetland["date"], y=df_wetland["water_change"],
                name="Water Spread Δ (%)",
                marker_color="rgba(56, 189, 248, 0.4)",
                marker_line_color="#0284c7",
                marker_line_width=1
            ),
            secondary_y=True
        )
    fig_wat.update_layout(
        **plotly_theme,
        title=dict(text=f"Surface Water Dynamics & Extent Contraction: {selected_name}", font=dict(size=14, weight=700)),
        xaxis_title="Observation Date",
        height=420,
        hovermode="x unified"
    )
    fig_wat.update_yaxes(title_text="MNDWI Value", secondary_y=False, gridcolor="#f1f5f9")
    fig_wat.update_yaxes(title_text="Water Spread Δ (%)", secondary_y=True, showgrid=False)
    st.plotly_chart(fig_wat, use_container_width=True)

with tab3:
    fig_sar = go.Figure()
    if "SAR_VV" in df_wetland.columns:
        fig_sar.add_trace(go.Scatter(
            x=df_wetland["date"], y=df_wetland["SAR_VV"],
            mode="lines+markers", name="SAR VV (dB)",
            line=dict(color="#b91c1c", width=2.2),
            marker=dict(size=4)
        ))
    if "SAR_VH" in df_wetland.columns:
        fig_sar.add_trace(go.Scatter(
            x=df_wetland["date"], y=df_wetland["SAR_VH"],
            mode="lines+markers", name="SAR VH (dB)",
            line=dict(color="#f59e0b", width=1.6, dash="dash"),
            marker=dict(size=4)
        ))
    fig_sar.update_layout(
        **plotly_theme,
        title=dict(text=f"Sentinel-1 C-Band SAR Dual-Polarization Backscatter: {selected_name}", font=dict(size=14, weight=700)),
        xaxis_title="Observation Date",
        yaxis_title="Backscatter Power (dB)",
        height=420,
        hovermode="x unified"
    )
    st.plotly_chart(fig_sar, use_container_width=True)
    st.caption("ℹ️ **Physical Remote Sensing Context**: Calm open surface water acts as a specular reflector directing radar beams away from the sensor (yielding low backscatter values). Wet soils and emergent vegetation produce rough volume or double-bounce scattering (higher backscatter).")

with tab4:
    fig_anom = go.Figure()
    if "NDVI_anomaly" in df_wetland.columns:
        fig_anom.add_trace(go.Scatter(
            x=df_wetland["date"], y=df_wetland["NDVI_anomaly"],
            mode="lines", name="NDVI Anomaly (Z-Score)",
            line=dict(color="#059669", width=2)
        ))
    if "MNDWI_anomaly" in df_wetland.columns:
        fig_anom.add_trace(go.Scatter(
            x=df_wetland["date"], y=df_wetland["MNDWI_anomaly"],
            mode="lines", name="MNDWI Anomaly (Z-Score)",
            line=dict(color="#0284c7", width=2)
        ))
    if "SAR_anomaly" in df_wetland.columns:
        fig_anom.add_trace(go.Scatter(
            x=df_wetland["date"], y=df_wetland["SAR_anomaly"],
            mode="lines", name="SAR Anomaly (Z-Score)",
            line=dict(color="#b91c1c", width=1.5, dash="dot")
        ))
    
    # Warning Threshold Lines
    fig_anom.add_hline(
        y=-1.0, line_dash="dash", line_color="#f59e0b",
        annotation_text="-1.0σ Warning Threshold",
        annotation_position="top right"
    )
    fig_anom.add_hline(
        y=-2.0, line_dash="dash", line_color="#ef4444",
        annotation_text="-2.0σ Severe Decline Threshold",
        annotation_position="bottom right"
    )
    
    fig_anom.update_layout(
        **plotly_theme,
        title=dict(text=f"Standardized Historical Anomalies (σ deviations from baseline): {selected_name}", font=dict(size=14, weight=700)),
        xaxis_title="Observation Date",
        yaxis_title="Standard Deviations (σ)",
        height=420,
        hovermode="x unified"
    )
    st.plotly_chart(fig_anom, use_container_width=True)
