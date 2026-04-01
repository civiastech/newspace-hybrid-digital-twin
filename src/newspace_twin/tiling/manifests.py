from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from newspace_twin.contracts.aoi import load_aoi_contract
from newspace_twin.datasets.splits import assign_splits
from newspace_twin.datasets.stats import compute_dataset_stats
from newspace_twin.settings.config import AppConfig
from newspace_twin.settings.paths import ensure_project_paths
from newspace_twin.tiling.grid import build_analysis_grid
from newspace_twin.tiling.raster_tiles import tile_feature_raster


def _load_yaml(path: str | Path) -> dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as handle:
        return yaml.safe_load(handle)


def _combine_tile_manifests(manifests: list[Path]) -> pd.DataFrame:
    frames = []

    for manifest in manifests:
        # Skip if file does not exist
        if not manifest.exists():
            continue

        # Skip empty files
        if manifest.stat().st_size == 0:
            continue

        # Try reading safely
        try:
            frame = pd.read_csv(manifest)
        except pd.errors.EmptyDataError:
            continue

        # Skip empty DataFrame
        if frame.empty:
            continue

        # Add feature group label
        feature_group = manifest.stem.replace("_tiles", "")
        frame["feature_group"] = feature_group

        frames.append(frame)

    # Combine safely
    if frames:
        return pd.concat(frames, ignore_index=True)

    return pd.DataFrame()


def run_dataset_build(config: AppConfig) -> dict[str, object]:
    paths = ensure_project_paths(config)
    project_root = Path(config.paths.project_root)
    tiling_cfg = _load_yaml(project_root / 'configs/datasets/tiling.yaml')['tiling']
    split_cfg = _load_yaml(project_root / 'configs/datasets/splits.yaml')['splits']

    aoi_path = project_root / 'configs/aois' / f'{config.active_aoi}.yaml'
    aoi = load_aoi_contract(aoi_path, config.paths.project_root)
    if not aoi.geometry_file:
        raise ValueError('AOI geometry file is required for dataset build.')
    aoi_geom_path = project_root / aoi.geometry_file

    manifest_root = Path(paths['manifests']) / config.active_aoi
    manifest_root.mkdir(parents=True, exist_ok=True)
    grid_path = manifest_root / 'analysis_grid.geojson'
    grid_result = build_analysis_grid(aoi_geom_path, grid_path, cell_size=float(tiling_cfg['grid_cell_size_m']))

    feature_root = Path(paths['features']) / config.active_aoi
    tile_root = Path(paths['processed']) / 'tiles' / config.active_aoi
    tile_manifests: list[Path] = []

    for feature_group in ['optical', 'sar']:
        group_dir = feature_root / feature_group
        for feature_raster in sorted(group_dir.glob('*.tif')):
            prefix = f"{feature_group}_{feature_raster.stem}"
            result = tile_feature_raster(feature_raster, grid_path, tile_root / prefix, prefix=prefix)
            tile_manifests.append(Path(result.manifest_uri))

    dataset_df = _combine_tile_manifests(tile_manifests)
    if dataset_df.empty:
        dataset_manifest_path = manifest_root / 'dataset_manifest.csv'
        dataset_df.to_csv(dataset_manifest_path, index=False)
        summary_path = manifest_root / 'dataset_build_status.json'
        summary_path.write_text(json.dumps({'status': 'empty', 'grid': asdict(grid_result)}, indent=2), encoding='utf-8')
        return {'dataset_manifest': str(dataset_manifest_path), 'dataset_summary': str(summary_path), 'grid': asdict(grid_result)}

    split_map = assign_splits(
        dataset_df['unit_id'].unique().tolist(),
        train=float(split_cfg['train']),
        val=float(split_cfg['val']),
        test=float(split_cfg['test']),
        seed=int(split_cfg['random_seed']),
    )
    dataset_df['split'] = dataset_df['unit_id'].map(split_map)
    dataset_df['task_type'] = 'wildfire_monitoring'
    dataset_df['sample_id'] = [f'sample_{i:06d}' for i in range(len(dataset_df))]
    dataset_df['label_uri'] = None
    dataset_df['feature_uri'] = dataset_df['tile_uri']

    dataset_manifest_path = manifest_root / 'dataset_manifest.csv'
    dataset_df.to_csv(dataset_manifest_path, index=False)

    stats = asdict(compute_dataset_stats(dataset_df))
    split_manifest_path = manifest_root / 'split_manifest.csv'
    dataset_df[['unit_id', 'split']].drop_duplicates().to_csv(split_manifest_path, index=False)
    summary = {
        'status': 'ok',
        'grid': asdict(grid_result),
        'dataset_manifest': str(dataset_manifest_path),
        'split_manifest': str(split_manifest_path),
        'stats': stats,
        'tile_manifest_count': len(tile_manifests),
    }
    summary_path = manifest_root / 'dataset_build_status.json'
    summary_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    return summary
