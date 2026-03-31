from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import Polygon

from newspace_twin.pipeline import run_pipeline


def _write_raster(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = np.ones((1, 10, 10), dtype=np.uint8)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=10,
        width=10,
        count=1,
        dtype="uint8",
        crs="EPSG:3763",
        transform=from_origin(0, 10, 1, 1),
    ) as dst:
        dst.write(data)


def test_ingestion_and_validation_pipeline(tmp_path: Path, monkeypatch) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()

    source_config = Path("configs/base.yaml").read_text(encoding="utf-8")
    adjusted_config = source_config.replace("project_root: .", f"project_root: {project_root.as_posix()}")
    config_path = project_root / "base.yaml"
    config_path.write_text(adjusted_config, encoding="utf-8")

    configs_dir = project_root / "configs"
    configs_dir.mkdir(parents=True)
    for rel in [
        "ingestion/sentinel1.yaml",
        "ingestion/sentinel2.yaml",
        "ingestion/uav.yaml",
        "ingestion/sensors.yaml",
        "ingestion/vectors.yaml",
        "preprocessing/timeseries.yaml",
        "preprocessing/vector.yaml",
    ]:
        target = configs_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((Path("configs") / rel).read_text(encoding="utf-8"), encoding="utf-8")

    _write_raster(project_root / "data/raw/sentinel1/wildfire_case_aoi/s1.tif")
    _write_raster(project_root / "data/raw/sentinel2/wildfire_case_aoi/s2.tif")
    _write_raster(project_root / "data/raw/uav/wildfire_case_aoi/uav.tif")

    sensor_df = pd.DataFrame({
        "sensor_id": ["a", "a"],
        "timestamp": ["2025-08-01T00:00:00Z", "2025-08-01T01:00:00Z"],
        "value": [1.0, 2.0],
    })
    sensor_path = project_root / "data/raw/sensors/wildfire_case_aoi/sensors.csv"
    sensor_path.parent.mkdir(parents=True, exist_ok=True)
    sensor_df.to_csv(sensor_path, index=False)

    gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[Polygon([(0,0), (1,0), (1,1), (0,1)])], crs="EPSG:3763")
    vector_path = project_root / "data/raw/vectors/wildfire_case_aoi/footprint.geojson"
    vector_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(vector_path, driver="GeoJSON")

    result_ingest = run_pipeline(str(config_path), "ingest")
    assert result_ingest["result"]["total_records_written"] == 5

    result_validate = run_pipeline(str(config_path), "validate")
    summary_path = Path(result_validate["result"]["summary_path"])
    assert summary_path.exists()
