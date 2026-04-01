from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_bounds

from newspace_twin.features.wildfire_features import (
    build_optical_feature_stack,
    build_sar_feature_stack,
    summarize_sensor_csv,
)
from newspace_twin.settings.config import AppConfig
from newspace_twin.settings.paths import ensure_project_paths


def _aoi_bounds_wgs84(aoi_geojson: Path) -> tuple[float, float, float, float]:
    gdf = gpd.read_file(aoi_geojson)
    if gdf.empty:
        raise ValueError(f"Empty AOI file: {aoi_geojson}")
    if gdf.crs is None:
        raise ValueError(f"AOI CRS missing: {aoi_geojson}")
    if gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    return tuple(gdf.total_bounds)


def _write_stack_tif(stack: np.ndarray, out_path: Path, bounds: tuple[float, float, float, float]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    bands, height, width = stack.shape
    transform = from_bounds(*bounds, width=width, height=height)

    with rasterio.open(
        out_path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=bands,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(stack.astype("float32"))


def run_feature_assembly(config: AppConfig) -> dict[str, object]:
    paths = ensure_project_paths(config)
    project_root = Path(config.paths.project_root)

    aoi_geojson = project_root / "data" / "raw" / "aoi" / f"{config.active_aoi}.geojson"
    bounds = _aoi_bounds_wgs84(aoi_geojson)

    processed_root = Path(paths["processed"])
    feature_root = Path(paths["features"]) / config.active_aoi
    feature_root.mkdir(parents=True, exist_ok=True)

    counts = {"optical": 0, "sar": 0, "terrain": 0, "temporal": 0}

    # ---------- Optical ----------
    s2_root = processed_root / "sentinel2" / config.active_aoi
    s2_pre = s2_root / "s2_pre_2024-07-10.tif.npz"
    s2_post = s2_root / "s2_post_2024-07-25.tif.npz"

    if s2_pre.exists() and s2_post.exists():
        optical_stack = build_optical_feature_stack(str(s2_pre), str(s2_post))
        out_path = feature_root / "optical" / "optical_stack.tif"
        _write_stack_tif(optical_stack, out_path, bounds)
        counts["optical"] = 1

    # ---------- SAR ----------
    s1_root = processed_root / "sentinel1" / config.active_aoi
    s1_pre = s1_root / "s1_pre_2024-07-08.tif.npz"
    s1_post = s1_root / "s1_post_2024-07-24.tif.npz"

    if s1_pre.exists() and s1_post.exists():
        sar_stack = build_sar_feature_stack(str(s1_pre), str(s1_post))
        out_path = feature_root / "sar" / "sar_stack.tif"
        _write_stack_tif(sar_stack, out_path, bounds)
        counts["sar"] = 1

    # ---------- Temporal ----------
    sensor_csv = processed_root / "sensors" / config.active_aoi / "sensor_timeseries_clean.csv"
    if sensor_csv.exists():
        df = pd.read_csv(sensor_csv)
        summary = summarize_sensor_csv(df)
        temporal_dir = feature_root / "temporal"
        temporal_dir.mkdir(parents=True, exist_ok=True)
        (temporal_dir / "sensor_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        counts["temporal"] = 1

    summary_path = feature_root / "feature_summary.json"
    summary_path.write_text(json.dumps({"counts": counts}, indent=2), encoding="utf-8")

    return {
        "feature_summary": str(summary_path),
        "counts": counts,
    }
