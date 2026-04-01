from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd


def export_prediction_geojson(
    grid_geojson: str | Path,
    predictions_csv: str | Path,
    output_geojson: str | Path,
) -> str:
    grid = gpd.read_file(grid_geojson)
    preds = pd.read_csv(predictions_csv)

    # keep only one row per unit for validation mapping
    preds = preds.sort_values(["unit_id", "confidence"], ascending=[True, False])
    preds = preds.drop_duplicates(subset=["unit_id"])

    merged = grid.merge(preds, on="unit_id", how="left")

    out_path = Path(output_geojson)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_file(out_path, driver="GeoJSON")
    return str(out_path)