from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml

from newspace_twin.features.optical import build_optical_features
from newspace_twin.features.sar import build_sar_features
from newspace_twin.features.temporal import build_temporal_features
from newspace_twin.features.terrain import build_terrain_features
from newspace_twin.settings.config import AppConfig
from newspace_twin.settings.paths import ensure_project_paths


def _load_yaml(path: str | Path) -> dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as handle:
        return yaml.safe_load(handle)


def run_feature_assembly(config: AppConfig) -> dict[str, object]:
    paths = ensure_project_paths(config)
    project_root = Path(config.paths.project_root)
    feature_root = Path(paths['features']) / config.active_aoi
    feature_root.mkdir(parents=True, exist_ok=True)

    optical_cfg = _load_yaml(project_root / 'configs/features/optical.yaml')
    results: dict[str, list[dict[str, Any]]] = {'optical': [], 'sar': [], 'terrain': [], 'temporal': []}

    sentinel2_root = Path(paths['processed']) / 'sentinel2' / config.active_aoi
    for raster_path in sorted(sentinel2_root.glob('*.tif')):
        output = feature_root / 'optical' / f'{raster_path.stem}_optical_features.tif'
        band_map = optical_cfg.get('features', {}).get('optical', {}).get('band_map')
        result = build_optical_features(raster_path, output, band_map=band_map)
        results['optical'].append(asdict(result))

    sentinel1_root = Path(paths['processed']) / 'sentinel1' / config.active_aoi
    for raster_path in sorted(sentinel1_root.glob('*.tif')):
        output = feature_root / 'sar' / f'{raster_path.stem}_sar_features.tif'
        result = build_sar_features(raster_path, output)
        results['sar'].append(asdict(result))

    uav_root = Path(paths['processed']) / 'uav' / config.active_aoi
    for raster_path in sorted(uav_root.glob('*dem*.tif')):
        output = feature_root / 'terrain' / f'{raster_path.stem}_terrain_features.tif'
        result = build_terrain_features(raster_path, output)
        results['terrain'].append(asdict(result))

    sensors_root = Path(paths['processed']) / 'sensors' / config.active_aoi
    for table_path in sorted(sensors_root.glob('*_clean.csv')):
        output = feature_root / 'temporal' / f'{table_path.stem}_temporal_features.csv'
        result = build_temporal_features(table_path, output)
        results['temporal'].append(asdict(result))

    summary = {
        'aoi_id': config.active_aoi,
        'counts': {k: len(v) for k, v in results.items()},
        'artifacts': results,
    }
    summary_path = feature_root / 'feature_summary.json'
    summary_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    return {'feature_summary': str(summary_path), 'counts': summary['counts']}
