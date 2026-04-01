from __future__ import annotations

from pathlib import Path

import geopandas as gpd


def recommend_action(row) -> str:
    risk_level = str(row.get("risk_level", "low"))
    trend = str(row.get("risk_trend", "stable"))
    escalation = int(row.get("escalation_flag", 0))
    persistence = int(row.get("persistence_flag", 0))

    if risk_level == "critical" and escalation == 1:
        return "immediate_field_intervention"
    if risk_level == "critical":
        return "urgent_site_review"
    if risk_level == "high" and escalation == 1:
        return "priority_inspection"
    if risk_level == "high" and persistence == 1:
        return "enhanced_monitoring"
    if risk_level == "medium" and trend == "increasing":
        return "scheduled_follow_up"
    return "routine_monitoring"


def build_alert_layer(input_geojson: str | Path, output_geojson: str | Path) -> str:
    gdf = gpd.read_file(input_geojson)

    gdf["recommended_action"] = gdf.apply(recommend_action, axis=1)
    gdf["alert_flag"] = (
        ((gdf["risk_level"] == "critical") | (gdf["escalation_flag"] == 1))
    ).astype(int)

    out_path = Path(output_geojson)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(out_path, driver="GeoJSON")
    return str(out_path)