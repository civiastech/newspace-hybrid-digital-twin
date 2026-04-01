from __future__ import annotations

from pathlib import Path

import yaml
from tests.fixtures.build_training_fixture import build_training_fixture

from newspace_twin.experiments.comparison import export_comparison_reports
from newspace_twin.experiments.error_analysis import export_error_analysis
from newspace_twin.experiments.runner import run_experiment


def test_run_experiment_and_reports(tmp_path: Path) -> None:
    manifest_csv, _features_csv = build_training_fixture(tmp_path)
    tracking_cfg = {
        'tracking': {
            'backend': 'local_jsonl',
            'experiment_name': 'pytest_exp',
            'run_name_prefix': 'baseline',
            'artifact_dir': str(tmp_path / 'artifacts'),
            'registry_path': str(tmp_path / 'experiment_registry.jsonl'),
            'enable_mlflow': False,
            'enable_wandb': False,
        }
    }
    tracking_path = tmp_path / 'tracking.yaml'
    tracking_path.write_text(yaml.safe_dump(tracking_cfg), encoding='utf-8')

    exp_cfg = {
        'task': 'segmentation',
        'manifest': str(manifest_csv),
        'train_config': 'configs/models/train_common.yaml',
        'tracking_config': str(tracking_path),
        'output_dir': str(tmp_path / 'checkpoints'),
    }
    exp_path = tmp_path / 'experiment.yaml'
    exp_path.write_text(yaml.safe_dump(exp_cfg), encoding='utf-8')

    result = run_experiment(exp_path)
    registry = Path(tracking_cfg['tracking']['registry_path'])
    assert registry.exists()
    assert Path(result['result']['checkpoint']).exists()
    assert Path(result['artifacts']['json']).exists()
    assert Path(result['artifacts']['md']).exists()

    error_csv = export_error_analysis(str(manifest_csv), result['result']['checkpoint'], 'segmentation', tmp_path / 'errors', split='val')
    assert Path(error_csv).exists()

    comparison = export_comparison_reports(registry, tmp_path / 'comparison')
    assert Path(comparison['json']).exists()
    assert Path(comparison['md']).exists()
    assert Path(comparison['csv']).exists()
