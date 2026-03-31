from __future__ import annotations

from dataclasses import asdict
from typing import Callable

from newspace_twin.features.assembler import run_feature_assembly
from newspace_twin.fusion.scoring import run_fusion_stage
from newspace_twin.ingestion.base import run_ingestion
from newspace_twin.preprocessing.alignment import run_preprocessing
from newspace_twin.qc.audit import run_validation
from newspace_twin.settings.config import AppConfig, load_config
from newspace_twin.tiling.manifests import run_dataset_build
from newspace_twin.twin.updater import run_twin_update


def _not_implemented(stage: str) -> dict[str, str]:
    return {'stage': stage, 'status': 'scaffolded', 'message': 'Stage scaffold is ready for implementation.'}


def run_pipeline(config_path: str, stage: str) -> dict[str, object]:
    config: AppConfig = load_config(config_path)

    stage_map: dict[str, Callable[[AppConfig], dict[str, object]]] = {
        'ingest': run_ingestion,
        'validate': run_validation,
        'preprocess': run_preprocessing,
        'features': run_feature_assembly,
        'tile': run_dataset_build,
        'build_dataset': run_dataset_build,
        'train': lambda cfg: _not_implemented('train'),
        'infer': lambda cfg: _not_implemented('infer'),
        'fuse': run_fusion_stage,
        'update_twin': run_twin_update,
        'report': lambda cfg: _not_implemented('report'),
    }

    if stage == 'all':
        outputs: dict[str, object] = {}
        for stage_name in ['ingest', 'validate', 'preprocess', 'features', 'build_dataset', 'fuse', 'update_twin']:
            outputs[stage_name] = stage_map[stage_name](config)
        return {'status': 'ok', 'pipeline': outputs}

    if stage not in stage_map:
        raise ValueError(f'Unsupported stage: {stage}')

    result = stage_map[stage](config)
    return {'status': 'ok', 'stage': stage, 'result': result, 'config': asdict(config)}
