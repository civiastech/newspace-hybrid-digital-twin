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


def color_from_risk_level(level: str) -> list[int]:
    level = str(level).lower()
    if level == "critical":
        return [220, 38, 38, 180]
    if level == "high":
        return [249, 115, 22, 180]
    if level == "medium":
        return [234, 179, 8, 180]
    return [34, 197, 94, 140]


def color_from_trend(trend: str) -> list[int]:
    trend = str(trend).lower()
    if trend == "increasing":
        return [220, 38, 38, 180]
    if trend == "decreasing":
        return [34, 197, 94, 180]
    return [234, 179, 8, 160]


def color_from_alert(flag: int) -> list[int]:
    return [220, 38, 38, 200] if int(flag) == 1 else [34, 197, 94, 120]


def polygon_layer_df(gdf: gpd.GeoDataFrame, color_fn, color_source_col: str) -> pd.DataFrame:
    rows = []

    for _, row in gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue

        if geom.geom_type == "Polygon":
            polygons = [geom]
        elif geom.geom_type == "MultiPolygon":
            polygons = list(geom.geoms)
        else:
            continue

        for poly in polygons:
            coords = list(poly.exterior.coords)
            polygon_coords = [[float(x), float(y)] for x, y in coords]

            rec = row.drop(labels="geometry").to_dict()
            rec["polygon"] = polygon_coords
            rec["fill_color"] = color_fn(row.get(color_source_col))
            rows.append(rec)

    return pd.DataFrame(rows)


def make_polygon_map(df: pd.DataFrame, tooltip_text: str):
    if df.empty:
        st.warning("No polygons to display.")
        return

    all_lons = []
    all_lats = []
    for poly in df["polygon"]:
        for pt in poly:
            all_lons.append(pt[0])
            all_lats.append(pt[1])

    center_lon = sum(all_lons) / len(all_lons)
    center_lat = sum(all_lats) / len(all_lats)

    layer = pdk.Layer(
        "PolygonLayer",
        data=df,
        get_polygon="polygon",
        get_fill_color="fill_color",
        get_line_color=[30, 30, 30, 180],
        line_width_min_pixels=1,
        pickable=True,
        stroked=True,
        filled=True,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=9,
        ),
        tooltip={"text": tooltip_text},
    )
    st.pydeck_chart(deck)


tab1, tab2, tab3 = st.tabs(["Risk Map", "Evolution Map", "Alerts Map"])

with tab1:
    st.subheader("Risk layer")
    gdf = load_geojson(risk_path)
    if gdf is None:
        st.warning("Risk layer not found.")
    else:
        df = polygon_layer_df(gdf, color_from_risk_level, "risk_level")
        make_polygon_map(
            df,
            "unit_id: {unit_id}\nrisk_level: {risk_level}\nrisk_score: {risk_score}\npred_class: {pred_class}",
        )
        st.dataframe(gdf.drop(columns="geometry", errors="ignore").head(50))

with tab2:
    st.subheader("Temporal evolution")
    gdf = load_geojson(evolution_path)
    if gdf is None:
        st.warning("Evolution layer not found.")
    else:
        df = polygon_layer_df(gdf, color_from_trend, "risk_trend")
        make_polygon_map(
            df,
            "unit_id: {unit_id}\nrisk_trend: {risk_trend}\nrisk_delta: {risk_delta}\nescalation_flag: {escalation_flag}",
        )
        st.dataframe(gdf.drop(columns="geometry", errors="ignore").head(50))

with tab3:
    st.subheader("Alert layer")
    gdf = load_geojson(alert_path)
    if gdf is None:
        st.warning("Alert layer not found.")
    else:
        df = polygon_layer_df(gdf, color_from_alert, "alert_flag")
        make_polygon_map(
            df,
            "unit_id: {unit_id}\nalert_flag: {alert_flag}\naction: {recommended_action}\nrisk_level: {risk_level}",
        )
        st.dataframe(gdf.drop(columns="geometry", errors="ignore").head(50))