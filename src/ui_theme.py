"""
src/ui_theme.py
Industry-standard UI design system and reusable styling components for Wetland Guard.
Provides cohesive executive typography, modern CSS variables, responsive metric cards,
standardized publication-quality Plotly chart themes, and unified status indicators.
"""
import streamlit as st
import plotly.graph_objects as go


def apply_custom_css():
    """
    Applies an enterprise-grade design system to Streamlit pages.
    Includes custom fonts, polished cards, elevated metrics, glassmorphic touches,
    refined tables, and responsive layouts.
    """
    st.markdown("""
    <style>
    /* Hide Streamlit built-in Deploy action; keep the remaining app toolbar intact. */
    div[data-testid="stAppDeployButton"] {
        display: none !important;
    }

    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --brand-primary: #065f46;
        --brand-primary-light: #10b981;
        --brand-dark: #0f172a;
        --brand-slate: #334155;
        --brand-border: #e2e8f0;
        --brand-bg-subtle: #f8fafc;
        --risk-high-bg: #fef2f2;
        --risk-high-text: #991b1b;
        --risk-high-border: #f87171;
        --risk-med-bg: #fffbeb;
        --risk-med-text: #92400e;
        --risk-med-border: #fcd34d;
        --risk-low-bg: #f0fdf4;
        --risk-low-text: #166534;
        --risk-low-border: #86efac;
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 96%;
    }

    /* Executive Page Header */
    .wg-header-container {
        background: linear-gradient(135deg, #064e3b 0%, #065f46 60%, #047857 100%);
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        color: white;
        box-shadow: 0 10px 25px -5px rgba(6, 78, 59, 0.25), 0 8px 10px -6px rgba(6, 78, 59, 0.2);
        position: relative;
        overflow: hidden;
    }
    .wg-header-container::after {
        content: "";
        position: absolute;
        top: -40px;
        right: -40px;
        width: 180px;
        height: 180px;
        background: radial-gradient(circle, rgba(16, 185, 129, 0.3) 0%, rgba(16, 185, 129, 0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    .wg-header-tagline {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        background: rgba(255, 255, 255, 0.16);
        backdrop-filter: blur(8px);
        padding: 4px 10px;
        border-radius: 20px;
        margin-bottom: 0.6rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .wg-header-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0 0 0.4rem 0;
        color: #ffffff !important;
        line-height: 1.2;
    }
    .wg-header-desc {
        font-size: 0.95rem;
        color: #e6f4ea;
        margin: 0;
        max-width: 900px;
        line-height: 1.45;
        font-weight: 400;
    }

    /* Enterprise Metric Card */
    .wg-metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        height: 100%;
    }
    .wg-metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.08);
        border-color: #cbd5e1;
    }
    .wg-metric-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 0.35rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .wg-metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.1;
        letter-spacing: -0.03em;
        margin-bottom: 0.3rem;
    }
    .wg-metric-subtext {
        font-size: 0.75rem;
        color: #94a3b8;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .wg-delta-chip {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 6px;
        line-height: 1.2;
    }
    .wg-delta-danger {
        background: #fee2e2;
        color: #991b1b;
    }
    .wg-delta-warning {
        background: #fef3c7;
        color: #92400e;
    }
    .wg-delta-success {
        background: #dcfce7;
        color: #166534;
    }
    .wg-delta-neutral {
        background: #f1f5f9;
        color: #475569;
    }

    /* Diagnostic Callout Card */
    .wg-callout-card {
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #059669;
        padding: 1.1rem 1.3rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .wg-callout-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.35rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .wg-callout-text {
        font-size: 0.85rem;
        color: #475569;
        line-height: 1.5;
        margin: 0;
    }

    /* Risk Badge Styles */
    .wg-badge-high {
        background: #fee2e2;
        color: #991b1b;
        border: 1px solid #f87171;
        padding: 3px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.78rem;
        letter-spacing: 0.04em;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    .wg-badge-med {
        background: #fef3c7;
        color: #92400e;
        border: 1px solid #fcd34d;
        padding: 3px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.78rem;
        letter-spacing: 0.04em;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    .wg-badge-low {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #86efac;
        padding: 3px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.78rem;
        letter-spacing: 0.04em;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }

    /* Section Subheadings */
    .wg-section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.01em;
        margin-top: 1rem;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .wg-section-subtitle {
        font-size: 0.82rem;
        color: #64748b;
        margin-bottom: 1rem;
    }

    /* Sidebar Refinement */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    .wg-sidebar-brand {
        padding: 0.75rem 0.5rem 1rem 0.5rem;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    .wg-sidebar-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #064e3b;
        letter-spacing: -0.02em;
        margin: 0;
        line-height: 1.2;
    }
    .wg-sidebar-sub {
        font-size: 0.75rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 3px;
    }
    .wg-pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        margin-right: 6px;
        box-shadow: 0 0 0 rgba(16, 185, 129, 0.4);
        animation: wgPulse 2s infinite;
    }
    @keyframes wgPulse {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.6); }
        70% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Tabs Elevation */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 0.85rem;
        color: #475569;
        background-color: transparent;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #065f46 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.06);
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
        transition: all 0.15s ease-in-out;
    }
    .stDownloadButton > button {
        border-radius: 8px;
        font-weight: 600;
        background: linear-gradient(135deg, #065f46 0%, #047857 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1.2rem;
        box-shadow: 0 2px 4px rgba(6, 95, 70, 0.2);
    }
    .stDownloadButton > button:hover {
        box-shadow: 0 4px 10px rgba(6, 95, 70, 0.3) !important;
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str, tag: str = "Decision Support System", show_badge: bool = True):
    """Renders a modern executive banner across pages."""
    badge_html = f'<div class="wg-header-tagline"><span class="wg-pulse-dot"></span>{tag}</div>' if show_badge else ""
    st.markdown(f"""
    <div class="wg-header-container">
        {badge_html}
        <h1 class="wg-header-title">{title}</h1>
        <p class="wg-header-desc">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Renders a cohesive enterprise sidebar brand and navigation telemetry."""
    st.sidebar.markdown("""
    <div class="wg-sidebar-brand">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
            <div style="background: linear-gradient(135deg, #064e3b, #047857); color: white; width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.1rem; box-shadow: 0 2px 6px rgba(6,78,59,0.3);">
                WG
            </div>
            <div>
                <h3 class="wg-sidebar-title">Wetland Guard</h3>
                <div class="wg-sidebar-sub">Geospatial AI Observatory</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 8px;">
            <span style="display: inline-flex; align-items: center; font-size: 0.72rem; font-weight: 700; color: #065f46; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 2px 8px; border-radius: 12px;">
                <span class="wg-pulse-dot"></span> Tamil Nadu • 15 Sites
            </span>
            <span style="font-size: 0.72rem; font-weight: 600; color: #475569; background: #f1f5f9; padding: 2px 8px; border-radius: 12px; border: 1px solid #e2e8f0;">
                v1.2 Active
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_plotly_theme():
    """
    Returns a unified, publication-grade Plotly layout template dictionary
    matching top-tier data journalism and scientific dashboards.
    """
    return dict(
        font=dict(family="Plus Jakarta Sans, -apple-system, sans-serif", size=12, color="#334155"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(
            bgcolor="#0f172a",
            font_size=12,
            font_family="Plus Jakarta Sans, sans-serif",
            font_color="#ffffff",
            bordercolor="rgba(255,255,255,0.1)"
        ),
        margin=dict(l=45, r=25, t=50, b=45),
        xaxis=dict(
            showgrid=True,
            gridcolor="#f1f5f9",
            zeroline=False,
            linecolor="#cbd5e1",
            tickfont=dict(size=11, color="#64748b")
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#f1f5f9",
            zeroline=True,
            zerolinecolor="#e2e8f0",
            linecolor="#cbd5e1",
            tickfont=dict(size=11, color="#64748b")
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#475569"),
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="#e2e8f0",
            borderwidth=1
        )
    )
