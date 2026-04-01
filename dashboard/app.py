from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd
import pydeck as pdk
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


def load_geojson(path: Path) -> gpd.GeoDataFrame | None:
    if not path.exists():
        return None
    gdf = gpd.read_file(path)
    if gdf.empty:
        return None
    if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    return gdf


def polygon_centroids_df(gdf: gpd.GeoDataFrame, value_col: str, label_col: str) -> pd.DataFrame:
    work = gdf.copy()
    work["centroid"] = work.geometry.centroid
    work["lon"] = work["centroid"].x
    work["lat"] = work["centroid"].y
    cols = ["lon", "lat", value_col, label_col]
    extra_cols = [c for c in ["unit_id", "pred_class", "true_class", "risk_score", "risk_level", "risk_trend", "alert_flag"] if c in work.columns]
    cols = list(dict.fromkeys(cols + extra_cols))
    return work[cols].copy()


def color_from_risk_level(level: str) -> list[int]:
    level = str(level).lower()
    if level == "critical":
        return [220, 38, 38, 180]
    if level == "high":
        return [249, 115, 22, 180]
    if level == "medium":
        return [234, 179, 8, 180]
    return [34, 197, 94, 180]


def color_from_trend(trend: str) -> list[int]:
    trend = str(trend).lower()
    if trend == "increasing":
        return [220, 38, 38, 180]
    if trend == "decreasing":
        return [34, 197, 94, 180]
    return [234, 179, 8, 180]


tab1, tab2, tab3 = st.tabs(["Risk Map", "Evolution Map", "Alerts Map"])

with tab1:
    st.subheader("Risk layer")
    gdf = load_geojson(risk_path)
    if gdf is None:
        st.warning("Risk layer not found.")
    else:
        df = polygon_centroids_df(gdf, "risk_score", "risk_level")
        df["color"] = df["risk_level"].apply(color_from_risk_level)

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position="[lon, lat]",
            get_radius=120,
            get_fill_color="color",
            pickable=True,
        )

        view_state = pdk.ViewState(
            latitude=float(df["lat"].mean()),
            longitude=float(df["lon"].mean()),
            zoom=9,
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "text": "unit_id: {unit_id}\nrisk_level: {risk_level}\nrisk_score: {risk_score}"
            },
        )
        st.pydeck_chart(deck)
        st.dataframe(gdf.drop(columns="geometry", errors="ignore").head(50))

with tab2:
    st.subheader("Temporal evolution")
    gdf = load_geojson(evolution_path)
    if gdf is None:
        st.warning("Evolution layer not found.")
    else:
        df = polygon_centroids_df(gdf, "risk_delta", "risk_trend")
        df["color"] = df["risk_trend"].apply(color_from_trend)

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position="[lon, lat]",
            get_radius=120,
            get_fill_color="color",
            pickable=True,
        )

        view_state = pdk.ViewState(
            latitude=float(df["lat"].mean()),
            longitude=float(df["lon"].mean()),
            zoom=9,
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "text": "unit_id: {unit_id}\nrisk_trend: {risk_trend}\nrisk_delta: {risk_delta}"
            },
        )
        st.pydeck_chart(deck)
        st.dataframe(gdf.drop(columns="geometry", errors="ignore").head(50))

with tab3:
    st.subheader("Alert layer")
    gdf = load_geojson(alert_path)
    if gdf is None:
        st.warning("Alert layer not found.")
    else:
        work = gdf.copy()
        work["centroid"] = work.geometry.centroid
        work["lon"] = work["centroid"].x
        work["lat"] = work["centroid"].y
        work["color"] = work["alert_flag"].apply(lambda x: [220, 38, 38, 200] if int(x) == 1 else [34, 197, 94, 120])

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=work,
            get_position="[lon, lat]",
            get_radius=130,
            get_fill_color="color",
            pickable=True,
        )

        view_state = pdk.ViewState(
            latitude=float(work["lat"].mean()),
            longitude=float(work["lon"].mean()),
            zoom=9,
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "text": "unit_id: {unit_id}\nalert_flag: {alert_flag}\naction: {recommended_action}"
            },
        )
        st.pydeck_chart(deck)
        st.dataframe(gdf.drop(columns="geometry", errors="ignore").head(50))