from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd

from newspace_twin.twin.risk import compute_risk_score, classify_priority


SEVERITY_TO_CONDITION = {
    0: 0.05,
    1: 0.30,
    2: 0.60,
    3: 0.90,
}


def _row_to_risk_inputs(row: pd.Series) -> dict:
    pred_raw = row.get("pred_class", 0)
    conf_raw = row.get("confidence", 0.0)

    pred_class = 0 if pd.isna(pred_raw) else int(pred_raw)
    confidence = 0.0 if pd.isna(conf_raw) else float(conf_raw)

    fused_condition_score = SEVERITY_TO_CONDITION.get(pred_class, 0.0)
    anomaly_score = fused_condition_score
    uncertainty_score = 1.0 - confidence
    consistency_score = confidence

    return {
        "fused_condition_score": fused_condition_score,
        "anomaly_score": anomaly_score,
        "uncertainty_score": uncertainty_score,
        "consistency_score": consistency_score,
    }


def build_risk_layer_from_predictions(
    prediction_geojson: str | Path,
    output_geojson: str | Path,
) -> str:
    gdf = gpd.read_file(prediction_geojson)

    risk_scores = []
    risk_levels = []
    priority_ranks = []
    fused_scores = []
    anomaly_scores = []
    uncertainty_scores = []
    consistency_scores = []

    for _, row in gdf.iterrows():
        vals = _row_to_risk_inputs(row)

        risk_score = compute_risk_score(
            fused_condition_score=vals["fused_condition_score"],
            anomaly_score=vals["anomaly_score"],
            uncertainty_score=vals["uncertainty_score"],
            consistency_score=vals["consistency_score"],
        )
        risk_level, priority_rank = classify_priority(risk_score)

        fused_scores.append(vals["fused_condition_score"])
        anomaly_scores.append(vals["anomaly_score"])
        uncertainty_scores.append(vals["uncertainty_score"])
        consistency_scores.append(vals["consistency_score"])
        risk_scores.append(risk_score)
        risk_levels.append(risk_level)
        priority_ranks.append(priority_rank)

    gdf["fused_condition_score"] = fused_scores
    gdf["anomaly_score"] = anomaly_scores
    gdf["uncertainty_score"] = uncertainty_scores
    gdf["consistency_score"] = consistency_scores
    gdf["risk_score"] = risk_scores
    gdf["risk_level"] = risk_levels
    gdf["priority_rank"] = priority_ranks

    out_path = Path(output_geojson)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(out_path, driver="GeoJSON")

    return str(out_path)