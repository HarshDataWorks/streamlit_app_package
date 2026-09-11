"""
Shared utilities for the Digital Analytics Streamlit app.
Loads pre-aggregated data (see /data_prep/build_processed_data.py for how
these were generated from the raw 6-table SQL Server database) and holds
the shared color palette so every page looks consistent.
"""
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# ---- Brand palette (matches the project's Power BI dashboards & final deck) ----
NAVY = "#1E2761"
GOLD = "#D9A441"
ICE = "#CADCFC"
GREY = "#6B7280"
RED = "#B0413E"
GREEN = "#2E7D32"

PLOTLY_TEMPLATE = "plotly_white"


@st.cache_data
def load_data():
    """Load all pre-aggregated CSVs. Cached so it only runs once per session."""
    data = {
        "monthly": pd.read_csv("data_processed/monthly_kpis.csv"),
        "product": pd.read_csv("data_processed/product_summary.csv"),
        "channel": pd.read_csv("data_processed/channel_summary.csv"),
        "device": pd.read_csv("data_processed/device_summary.csv"),
        "landing": pd.read_csv("data_processed/landing_page_summary.csv"),
        "funnel": pd.read_csv("data_processed/funnel_summary.csv"),
        "model_features": pd.read_csv("data_processed/session_model_features.csv"),
        "seasonality": pd.read_csv("data_processed/seasonality.csv"),
        "order_value_stats": pd.read_csv("data_processed/order_value_stats.csv"),
        "order_value_raw": pd.read_csv("data_processed/order_value_raw.csv"),
        "new_vs_repeat": pd.read_csv("data_processed/new_vs_repeat.csv"),
        "device_monthly": pd.read_csv("data_processed/device_monthly_trend.csv"),
    }
    return data


def kpi_card(col, label, value, delta=None):
    """Render one KPI using Streamlit's native metric widget."""
    col.metric(label, value, delta)


def styled_fig(fig, height=420):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        font=dict(family="Arial", color=NAVY),
        title_font=dict(size=16, color=NAVY),
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig


def page_header(title, subtitle):
    st.markdown(f"<h1 style='color:{NAVY};'>{title}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{GREY}; font-size:1.05rem;'>{subtitle}</p>", unsafe_allow_html=True)
    st.divider()
