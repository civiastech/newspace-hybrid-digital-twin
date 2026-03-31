from __future__ import annotations

import json
from pathlib import Path

import typer
import yaml

from newspace_twin.models.anomaly.train import train_anomaly_model
from newspace_twin.models.segmentation.train import train_segmentation
from newspace_twin.models.severity.train import train_severity_classifier
from newspace_twin.training.engine import TrainConfig

app = typer.Typer(help='Train baseline models for Deliverable 2A.')


def _load_yaml(path: str | Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding='utf-8'))


@app.command()
def main(
    task: str = typer.Option(..., help='segmentation | severity | anomaly'),
    manifest: str = typer.Option(..., help='Manifest CSV for image tasks or features CSV for anomaly.'),
    train_config: str = typer.Option('configs/models/train_common.yaml'),
    output_dir: str = typer.Option('data/reports/checkpoints'),
) -> None:
    cfg_raw = _load_yaml(train_config)
    cfg = TrainConfig(
        epochs=int(cfg_raw.get('epochs', 2)),
        batch_size=int(cfg_raw.get('batch_size', 4)),
        learning_rate=float(cfg_raw.get('learning_rate', 1e-3)),
        weight_decay=float(cfg_raw.get('weight_decay', 1e-4)),
        device=str(cfg_raw.get('device', 'cpu')),
    )
    if task == 'segmentation':
        result = train_segmentation(manifest, output_dir, cfg)
    elif task == 'severity':
        result = train_severity_classifier(manifest, output_dir, cfg)
    elif task == 'anomaly':
        result = train_anomaly_model(manifest, output_dir, cfg)
    else:
        raise typer.BadParameter(f'Unsupported task: {task}')
    typer.echo(json.dumps(result, indent=2))


if __name__ == '__main__':
    app()
