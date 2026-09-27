"""
pages/1_Dashboard.py
Regional GIS Map and Risk Prioritisation Dashboard for Tamil Nadu Wetlands.
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from src.dashboard_utils import get_wetland_boundaries, get_all_observations, compute_scores_for_date
from src.ui_theme import apply_custom_css, render_header, render_sidebar

st.set_page_config(page_title="Regional Dashboard | Wetland Guard", page_icon="🗺️", layout="wide")

# Apply enterprise styling
apply_custom_css()
render_sidebar()

# Page Executive Header
render_header(
    title="Wetland Guard — Regional Monitoring Map",
    subtitle="Geospatial Early-Warning and Degradation Risk Prioritisation across 15 Ramsar & NWIA Wetlands in Tamil Nadu",
    tag="Regional GIS Map & KPIs"
)

gdf = get_wetland_boundaries()
df_all = get_all_observations()

if gdf is None or df_all is None:
    st.error("Wetland data could not be loaded. Please ensure data/features/wetland_features.csv exists.")
    st.stop()

# Time Filter Selector Bar
all_dates = sorted(df_all["date"].dt.strftime("%Y-%m-%d").unique())

st.markdown("""
<div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem 1.4rem; margin-bottom: 1.2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <span style="font-size: 0.85rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 6px;">
            <span>📅</span> Temporal Observation Window
        </span>
        <span style="font-size: 0.75rem; color: #64748b; font-weight: 500;">Monthly Composites (2021–2024)</span>
    </div>
</div>
""", unsafe_allow_html=True)

col_time1, col_time2 = st.columns([3, 1])
with col_time1:
    selected_date_str = st.select_slider(
        "Select Satellite Observation Period:",
        options=all_dates,
        value=all_dates[-1],
        label_visibility="collapsed"
    )
with col_time2:
    st.markdown(f"""
    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 8px 12px; text-align: center;">
        <div style="font-size: 0.7rem; font-weight: 700; color: #166534; text-transform: uppercase;">Active Date</div>
        <div style="font-size: 1.05rem; font-weight: 800; color: #14532d;">{selected_date_str}</div>
    </div>
    """, unsafe_allow_html=True)

# Compute scores for selected date
scores_df = compute_scores_for_date(df_all, selected_date_str)

# KPI Cards
n_total = len(scores_df)
n_high = (scores_df["risk_category"] == "HIGH").sum()
n_med = (scores_df["risk_category"] == "MEDIUM").sum()
n_low = (scores_df["risk_category"] == "LOW").sum()
avg_dq = scores_df["data_quality"].mean() if "data_quality" in scores_df.columns else 0.95

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="wg-metric-card">
        <div class="wg-metric-label">Monitored Sites <span>📍</span></div>
        <div class="wg-metric-value">{n_total}</div>
        <div class="wg-metric-subtext"><span class="wg-delta-chip wg-delta-neutral">Tamil Nadu</span> All Sites</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    high_chip_cls = "wg-delta-danger" if n_high > 0 else "wg-delta-neutral"
    st.markdown(f"""
    <div class="wg-metric-card">
        <div class="wg-metric-label">High Risk <span>🚨</span></div>
        <div class="wg-metric-value" style="color: #b91c1c;">{n_high}</div>
        <div class="wg-metric-subtext"><span class="wg-delta-chip {high_chip_cls}">Score ≥ 70</span> Urgent Action</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    med_chip_cls = "wg-delta-warning" if n_med > 0 else "wg-delta-neutral"
    st.markdown(f"""
    <div class="wg-metric-card">
        <div class="wg-metric-label">Medium Risk <span>⚠️</span></div>
        <div class="wg-metric-value" style="color: #b45309;">{n_med}</div>
        <div class="wg-metric-subtext"><span class="wg-delta-chip {med_chip_cls}">Score 35–69</span> Watchlist</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="wg-metric-card">
        <div class="wg-metric-label">Low Risk <span>🌿</span></div>
        <div class="wg-metric-value" style="color: #15803d;">{n_low}</div>
        <div class="wg-metric-subtext"><span class="wg-delta-chip wg-delta-success">Score &lt; 35</span> Stable</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="wg-metric-card">
        <div class="wg-metric-label">Avg Data Quality <span>🛰️</span></div>
        <div class="wg-metric-value">{avg_dq:.1%}</div>
        <div class="wg-metric-subtext"><span class="wg-delta-chip wg-delta-success">Confidence</span> Sensor Integrity</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Layout: Map on left (65%), Detail Inspector on right (35%)
col_map, col_detail = st.columns([65, 35])

with col_map:
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <div class="wg-section-title" style="margin: 0;">
            <span>🗺️</span> Regional GIS Degradation Risk Map
        </div>
        <div style="font-size: 0.78rem; color: #64748b; font-weight: 500;">
            Circle size = Area (ha) • Circle color = Degradation Risk
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize Folium Map centered on Tamil Nadu using OpenStreetMap (No API Key Required)
    m = folium.Map(location=[10.85, 78.75], zoom_start=7, tiles="OpenStreetMap")
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="Satellite View (Esri)"
    ).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri Topographic",
        name="Topographic View (Esri)"
    ).add_to(m)

    # Add markers with modern popup HTML
    for _, row in scores_df.iterrows():
        lat = row["latitude"]
        lon = row["longitude"]
        score = row["risk_score"]
        cat = row["risk_category"]
        wname = row["wetland_name"]
        wid = row["wetland_id"]
        area = row.get("area", 100)
        
        # Color mapping with modern hexes
        if cat == "HIGH":
            color = "#b91c1c"
            fill_color = "#ef4444"
            badge_bg = "#fee2e2"
            badge_txt = "#991b1b"
        elif cat == "MEDIUM":
            color = "#b45309"
            fill_color = "#f59e0b"
            badge_bg = "#fef3c7"
            badge_txt = "#92400e"
        else:
            color = "#15803d"
            fill_color = "#22c55e"
            badge_bg = "#dcfce7"
            badge_txt = "#166534"
            
        radius = max(8, min(24, 7 + (area ** 0.35)))
        
        popup_html = f"""
        <div style="font-family: 'Plus Jakarta Sans', -apple-system, sans-serif; min-width: 220px; padding: 4px;">
            <div style="font-size: 1.05rem; font-weight: 800; color: #0f172a; margin-bottom: 3px;">{wname}</div>
            <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 8px;">ID: <code>{wid}</code> • {area:,.1f} ha</div>
            <div style="display: flex; align-items: center; justify-content: space-between; background: {badge_bg}; border: 1px solid {color}40; border-radius: 8px; padding: 6px 10px; margin-bottom: 8px;">
                <span style="font-size: 0.75rem; font-weight: 700; color: {badge_txt};">{cat} RISK</span>
                <span style="font-size: 1.1rem; font-weight: 800; color: {badge_txt};">{score:.1f} <span style="font-size: 0.75rem;">/ 100</span></span>
            </div>
            <div style="font-size: 0.75rem; color: #334155; line-height: 1.5; border-top: 1px solid #f1f5f9; padding-top: 6px;">
                <b>NDVI:</b> {row.get('NDVI', 0):.2f} | <b>MNDWI:</b> {row.get('MNDWI', 0):.2f}<br>
                <b>Key Evidence:</b> {row.get('top_reason', 'Normal baseline')}
            </div>
        </div>
        """
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color=color,
            weight=2.5,
            fill=True,
            fill_color=fill_color,
            fill_opacity=0.8,
            tooltip=f"{wname} — {cat} ({score:.1f}/100)",
            popup=folium.Popup(popup_html, max_width=320)
        ).add_to(m)

    folium.LayerControl(position="topright").add_to(m)

    map_data = st_folium(m, width="100%", height=530, returned_objects=["last_object_clicked"])

    # Map Legend Bar
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; gap: 24px; background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 16px; margin-top: 8px;">
        <div style="display: flex; align-items: center; gap: 6px; font-size: 0.78rem; font-weight: 600; color: #991b1b;">
            <span style="display: inline-block; width: 12px; height: 12px; background: #ef4444; border-radius: 50%; border: 2px solid #b91c1c;"></span>
            High Risk (≥ 70)
        </div>
        <div style="display: flex; align-items: center; gap: 6px; font-size: 0.78rem; font-weight: 600; color: #92400e;">
            <span style="display: inline-block; width: 12px; height: 12px; background: #f59e0b; border-radius: 50%; border: 2px solid #b45309;"></span>
            Medium Risk (35–69)
        </div>
        <div style="display: flex; align-items: center; gap: 6px; font-size: 0.78rem; font-weight: 600; color: #166534;">
            <span style="display: inline-block; width: 12px; height: 12px; background: #22c55e; border-radius: 50%; border: 2px solid #15803d;"></span>
            Low Risk (&lt; 35)
        </div>
        <div style="font-size: 0.75rem; color: #64748b; border-left: 1px solid #e2e8f0; padding-left: 16px;">
            Marker radius scales with surface area (ha)
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_detail:
    st.markdown("""
    <div class="wg-section-title" style="margin-top: 0;">
        <span>🔍</span> Site Diagnostic Inspector
    </div>
    """, unsafe_allow_html=True)
    
    # Selection dropdown for inspection
    wetland_names = list(scores_df["wetland_name"])
    selected_name = st.selectbox("Select Wetland to Inspect:", wetland_names, index=0)
    
    selected_row = scores_df[scores_df["wetland_name"] == selected_name].iloc[0]
    
    cat = selected_row["risk_category"]
    score = selected_row["risk_score"]
    
    if cat == "HIGH":
        badge_style = "background: linear-gradient(135deg, #fef2f2, #fee2e2); color: #991b1b; border: 1px solid #f87171;"
        bar_color = "#ef4444"
    elif cat == "MEDIUM":
        badge_style = "background: linear-gradient(135deg, #fffbeb, #fef3c7); color: #92400e; border: 1px solid #fcd34d;"
        bar_color = "#f59e0b"
    else:
        badge_style = "background: linear-gradient(135deg, #f0fdf4, #dcfce7); color: #166534; border: 1px solid #86efac;"
        bar_color = "#22c55e"
        
    st.markdown(f"""
    <div style="padding: 1.25rem; border-radius: 12px; {badge_style} text-align: center; margin-bottom: 1rem; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
        <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.06em;">Degradation Risk Assessment</div>
        <div style="font-size: 2.5rem; font-weight: 800; margin: 0.1rem 0; line-height: 1;">
            {score:.1f} <span style="font-size: 1.1rem; font-weight: 600;">/ 100</span>
        </div>
        <div style="font-size: 1rem; font-weight: 800; letter-spacing: 0.04em;">{cat} RISK CATEGORY</div>
        <div style="background: rgba(0,0,0,0.08); height: 6px; border-radius: 3px; margin: 10px 10% 0 10%; overflow: hidden;">
            <div style="background: {bar_color}; height: 100%; width: {min(100, max(0, score))}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metadata Details Grid
    st.markdown(f"""
    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; font-size: 0.82rem; color: #334155; line-height: 1.6; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 4px;">
            <span style="color: #64748b;">Wetland Identifier</span>
            <span style="font-weight: 700;"><code>{selected_row['wetland_id']}</code></span>
        </div>
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 4px 0;">
            <span style="color: #64748b;">Geographic Coordinates</span>
            <span style="font-weight: 600;">{selected_row['latitude']:.4f}° N, {selected_row['longitude']:.4f}° E</span>
        </div>
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 4px 0;">
            <span style="color: #64748b;">Surface Area</span>
            <span style="font-weight: 600;">{selected_row.get('area', 0):,.1f} hectares</span>
        </div>
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 4px 0;">
            <span style="color: #64748b;">Observation Period</span>
            <span style="font-weight: 600;">{selected_date_str}</span>
        </div>
        <div style="display: flex; justify-content: space-between; padding-top: 4px;">
            <span style="color: #64748b;">Sensor Data Quality</span>
            <span style="font-weight: 700; color: #166534;">{selected_row.get('data_quality', 0.9):.1%} Confidence</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="font-size: 0.85rem; font-weight: 700; color: #0f172a; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
        <span>📋</span> Quantitative Evidence-Based Reason Codes
    </div>
    """, unsafe_allow_html=True)

    reasons = selected_row.get("evidence_reasons", "").split("; ")
    for r in reasons:
        if r.strip():
            st.markdown(f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 3px solid #0284c7; border-radius: 6px; padding: 6px 10px; font-size: 0.78rem; color: #334155; margin-bottom: 6px; line-height: 1.4;">
                {r.strip()}
            </div>
            """, unsafe_allow_html=True)
            
    st.info("💡 Open **2_Wetland_Explorer** for multi-year sensor curves and anomaly trajectories.")
