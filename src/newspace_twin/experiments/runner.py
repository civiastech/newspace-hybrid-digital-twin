from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from newspace_twin.models.anomaly.train import train_anomaly_model
from newspace_twin.models.segmentation.train import train_segmentation
from newspace_twin.models.severity.train import train_severity_classifier
from newspace_twin.training.engine import TrainConfig

from .reports import write_json_report, write_markdown_report
from .tracker import RunTracker, TrackingConfig


def _load_yaml(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding='utf-8'))


def _train_cfg(path: str | Path) -> TrainConfig:
    raw = _load_yaml(path)
    return TrainConfig(
        epochs=int(raw.get('epochs', 2)),
        batch_size=int(raw.get('batch_size', 4)),
        learning_rate=float(raw.get('learning_rate', 1e-3)),
        weight_decay=float(raw.get('weight_decay', 1e-4)),
        device=str(raw.get('device', 'cpu')),
    )


def _tracking_cfg(path: str | Path) -> TrackingConfig:
    raw = _load_yaml(path).get('tracking', {})
    return TrackingConfig(**raw)


def run_experiment(experiment_config_path: str | Path) -> dict[str, Any]:
    exp = _load_yaml(experiment_config_path)
    task = str(exp['task'])
    manifest = str(exp['manifest'])
    output_dir = str(exp.get('output_dir', 'data/reports/checkpoints'))
    train_cfg = _train_cfg(exp['train_config'])
    tracking_cfg = _tracking_cfg(exp['tracking_config'])
    params = {
        'task': task,
        'manifest': manifest,
        'epochs': train_cfg.epochs,
        'batch_size': train_cfg.batch_size,
        'learning_rate': train_cfg.learning_rate,
        'weight_decay': train_cfg.weight_decay,
        'device': train_cfg.device,
        'experiment_config': str(experiment_config_path),
    }
    with RunTracker(tracking_cfg, task=task, params=params) as tracker:
        if task == 'segmentation':
            result = train_segmentation(manifest, output_dir, train_cfg)
        elif task == 'severity':
            result = train_severity_classifier(manifest, output_dir, train_cfg)
        elif task == 'anomaly':
            result = train_anomaly_model(manifest, output_dir, train_cfg)
        else:
            raise ValueError(f'Unsupported task: {task}')

        tracker.log_metrics({k: float(v) for k, v in result.get('metrics', {}).items()})
        tracker.log_artifact(result['checkpoint'])
        report_dir = Path(tracking_cfg.artifact_dir) / tracker.run_id
        json_path = write_json_report(report_dir / 'result.json', result)
        md_path = write_markdown_report(report_dir / 'result.md', f'{task.title()} experiment result', result)
        tracker.log_artifact(json_path)
        tracker.log_artifact(md_path)
        tracker.set_tags({'task': task, 'deliverable': '2B'})
        return {'run': tracker.to_record(), 'result': result, 'artifacts': {'json': json_path, 'md': md_path}}
