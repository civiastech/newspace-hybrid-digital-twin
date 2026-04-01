from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import Polygon

from newspace_twin.pipeline import run_pipeline


def _write_raster(path: Path, crs: str = 'EPSG:4326') -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = np.ones((1, 10, 10), dtype=np.uint8)
    with rasterio.open(
        path,
        'w',
        driver='GTiff',
        height=10,
        width=10,
        count=1,
        dtype='uint8',
        crs=crs,
        transform=from_origin(0, 10, 1, 1),
    ) as dst:
        dst.write(data)



def test_preprocessing_pipeline(tmp_path: Path) -> None:
    project_root = tmp_path / 'project'
    project_root.mkdir()

    source_config = Path('configs/base.yaml').read_text(encoding='utf-8')
    adjusted_config = source_config.replace('project_root: .', f'project_root: {project_root.as_posix()}')
    config_path = project_root / 'base.yaml'
    config_path.write_text(adjusted_config, encoding='utf-8')

    for rel in [
        'configs/ingestion/sentinel1.yaml',
        'configs/ingestion/sentinel2.yaml',
        'configs/ingestion/uav.yaml',
        'configs/ingestion/sensors.yaml',
        'configs/ingestion/vectors.yaml',
        'configs/preprocessing/raster.yaml',
        'configs/preprocessing/timeseries.yaml',
        'configs/preprocessing/vector.yaml',
        'configs/aois/wildfire_case_aoi.yaml',
    ]:
        src = Path(rel)
        dst = project_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')

    aoi = gpd.GeoDataFrame({'id': [1]}, geometry=[Polygon([(0, 0), (5, 0), (5, 5), (0, 5)])], crs='EPSG:4326')
    aoi_path = project_root / 'data/raw/aoi/wildfire_case_aoi.geojson'
    aoi_path.parent.mkdir(parents=True, exist_ok=True)
    aoi.to_file(aoi_path, driver='GeoJSON')

    _write_raster(project_root / 'data/raw/sentinel1/wildfire_case_aoi/s1.tif')
    _write_raster(project_root / 'data/raw/sentinel2/wildfire_case_aoi/s2.tif')
    _write_raster(project_root / 'data/raw/uav/wildfire_case_aoi/uav.tif')

    sensor_df = pd.DataFrame({
        'sensor_id': ['a', 'a', 'a'],
        'timestamp': ['2025-08-01T00:10:00Z', '2025-08-01T00:40:00Z', '2025-08-01T01:10:00Z'],
        'value': [1.0, 3.0, 5.0],
    })
    sensor_path = project_root / 'data/raw/sensors/wildfire_case_aoi/sensors.csv'
    sensor_path.parent.mkdir(parents=True, exist_ok=True)
    sensor_df.to_csv(sensor_path, index=False)

    gdf = gpd.GeoDataFrame({'id': [1]}, geometry=[Polygon([(0,0), (1,0), (1,1), (0,1)])], crs='EPSG:4326')
    vector_path = project_root / 'data/raw/vectors/wildfire_case_aoi/footprint.geojson'
    vector_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(vector_path, driver='GeoJSON')

    run_pipeline(str(config_path), 'ingest')
    result = run_pipeline(str(config_path), 'preprocess')
    report_path = Path(result['result']['preprocessing_report'])
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding='utf-8'))
    assert report['counts']['raster'] == 3
    assert report['counts']['vector'] == 1
    assert report['counts']['timeseries'] == 1

    processed_sensor = project_root / 'data/processed/sensors/wildfire_case_aoi/sensors_clean.csv'
    assert processed_sensor.exists()
    processed_df = pd.read_csv(processed_sensor)
    assert len(processed_df) == 2
