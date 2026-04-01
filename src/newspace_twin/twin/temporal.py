from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd


def classify_trend(delta: float, up_threshold: float = 0.10, down_threshold: float = -0.10) -> str:
    if delta >= up_threshold:
        return "increasing"
    if delta <= down_threshold:
        return "decreasing"
    return "stable"


def build_temporal_risk_state(
    previous_geojson: str | Path,
    current_geojson: str | Path,
    output_geojson: str | Path,
) -> str:
    prev_gdf = gpd.read_file(previous_geojson)
    curr_gdf = gpd.read_file(current_geojson)

    prev_cols = [
        "unit_id",
        "risk_score",
        "risk_level",
        "priority_rank",
    ]
    prev_df = prev_gdf[prev_cols].copy()
    prev_df = prev_df.rename(
        columns={
            "risk_score": "prev_risk_score",
            "risk_level": "prev_risk_level",
            "priority_rank": "prev_priority_rank",
        }
    )

    merged = curr_gdf.merge(prev_df, on="unit_id", how="left")

    merged["prev_risk_score"] = merged["prev_risk_score"].fillna(0.0)
    merged["risk_delta"] = merged["risk_score"] - merged["prev_risk_score"]
    merged["risk_trend"] = merged["risk_delta"].apply(classify_trend)

    merged["escalation_flag"] = (
        (merged["risk_trend"] == "increasing") & (merged["risk_score"] >= 0.5)
    ).astype(int)

    merged["persistence_flag"] = (
        (merged["risk_score"] >= 0.5) & (merged["prev_risk_score"] >= 0.5)
    ).astype(int)

    out_path = Path(output_geojson)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_file(out_path, driver="GeoJSON")

    return str(out_path)
