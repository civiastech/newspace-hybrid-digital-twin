from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml

from newspace_twin.contracts.aoi import load_aoi_contract
from newspace_twin.preprocessing.raster import preprocess_raster
from newspace_twin.preprocessing.timeseries import preprocess_timeseries
from newspace_twin.preprocessing.vector import preprocess_vector
from newspace_twin.registry.repository import read_registry_snapshot
from newspace_twin.settings.config import AppConfig
from newspace_twin.settings.paths import ensure_project_paths


RASTER_MODALITIES = {'sentinel1', 'sentinel2', 'uav'}
VECTOR_MODALITIES = {'vectors'}
TIMESERIES_MODALITIES = {'sensors'}


def _load_yaml(path: str | Path) -> dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as handle:
        return yaml.safe_load(handle)


def _processed_output_path(paths: dict[str, Path], aoi_id: str, modality: str, source_uri: str, suffix: str) -> Path:
    return Path(paths['processed']) / modality / aoi_id / f"{Path(source_uri).stem}{suffix}"


def run_preprocessing(config: AppConfig) -> dict[str, object]:
    paths = ensure_project_paths(config)
    manifests_root = Path(paths['manifests']) / config.active_aoi
    output_root = Path(paths['processed'])
    output_root.mkdir(parents=True, exist_ok=True)

    raster_rules = _load_yaml(Path(config.paths.project_root) / 'configs/preprocessing/raster.yaml')['raster']
    vector_rules = _load_yaml(config.validation_configs['vectors'])['vector_validation']
    ts_rules = _load_yaml(config.validation_configs['sensors'])
    aoi_path = Path(config.paths.project_root) / 'configs/aois' / f'{config.active_aoi}.yaml'
    aoi_contract = load_aoi_contract(aoi_path, config.paths.project_root)
    aoi_geometry_path = Path(config.paths.project_root) / aoi_contract.geometry_file if aoi_contract.geometry_file else None

    results: dict[str, list[dict[str, Any]]] = {'raster': [], 'vector': [], 'timeseries': []}

    for manifest_path in sorted(manifests_root.glob('*_registry.csv')):
        modality = manifest_path.stem.replace('_registry', '')
        records = read_registry_snapshot(manifest_path)
        for record in records:
            source_uri = record['source_uri']
            if modality in RASTER_MODALITIES:
                output_path = _processed_output_path(paths, config.active_aoi, modality, source_uri, '.tif')
                result = preprocess_raster(
                    source_uri,
                    output_path,
                    target_epsg=config.runtime.target_crs,
                    aoi_path=aoi_geometry_path,
                    clip_to_aoi=bool(raster_rules.get('clip_to_aoi', True)),
                    resampling=str(raster_rules.get('resampling', 'bilinear')),
                )
                results['raster'].append(asdict(result))
            elif modality in VECTOR_MODALITIES:
                output_path = _processed_output_path(paths, config.active_aoi, modality, source_uri, '.geojson')
                result = preprocess_vector(
                    source_uri,
                    output_path,
                    target_epsg=config.runtime.target_crs,
                    allow_repair=bool(vector_rules.get('allow_repair', True)),
                )
                results['vector'].append(asdict(result))
            elif modality in TIMESERIES_MODALITIES:
                output_path = _processed_output_path(paths, config.active_aoi, modality, source_uri, '_clean.csv')
                result = preprocess_timeseries(source_uri, output_path, rules=ts_rules)
                results['timeseries'].append(asdict(result))

    report = {
        'aoi': asdict(aoi_contract),
        'counts': {key: len(value) for key, value in results.items()},
        'artifacts': results,
    }
    report_path = Path(paths['interim']) / config.active_aoi / 'preprocessing_report.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open('w', encoding='utf-8') as handle:
        json.dump(report, handle, indent=2)
    return {'preprocessing_report': str(report_path), 'processed_root': str(output_root), 'counts': report['counts']}
