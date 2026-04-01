from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd
import streamlit as st

st.set_page_config(page_title="NewSpace Digital Twin Dashboard", layout="wide")

st.title("NewSpace Hybrid Digital Twin Dashboard")

risk_path = Path("data/twin/wildfire_case_aoi/risk_layer.geojson")
evolution_path = Path("data/twin/wildfire_case_aoi/risk_evolution.geojson")
alert_path = Path("data/twin/wildfire_case_aoi/alert_layer.geojson")

col1, col2, col3 = st.columns(3)
col1.write(f"Risk layer exists: {risk_path.exists()}")
col2.write(f"Evolution layer exists: {evolution_path.exists()}")
col3.write(f"Alert layer exists: {alert_path.exists()}")

tab1, tab2, tab3 = st.tabs(["Risk", "Evolution", "Alerts"])

with tab1:
    if risk_path.exists():
        gdf = gpd.read_file(risk_path)
        st.subheader("Risk layer")
        st.dataframe(gdf.drop(columns="geometry", errors="ignore").head(50))
    else:
        st.warning("Risk layer not found.")

with tab2:
    if evolution_path.exists():
        gdf = gpd.read_file(evolution_path)
        st.subheader("Temporal evolution")
        st.dataframe(gdf.drop(columns="geometry", errors="ignore").head(50))
    else:
        st.warning("Evolution layer not found.")

with tab3:
    if alert_path.exists():
        gdf = gpd.read_file(alert_path)
        st.subheader("Alert layer")
        st.dataframe(gdf.drop(columns="geometry", errors="ignore").head(50))
    else:
        st.warning("Alert layer not found.")