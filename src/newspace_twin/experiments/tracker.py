from __future__ import annotations

import json
import os
from contextlib import AbstractContextManager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(slots=True)
class TrackingConfig:
    backend: str = 'local_jsonl'
    experiment_name: str = 'default_experiment'
    run_name_prefix: str = 'run'
    artifact_dir: str = 'data/reports/experiments/artifacts'
    registry_path: str = 'data/reports/experiments/experiment_registry.jsonl'
    enable_mlflow: bool = False
    mlflow_tracking_uri: str | None = None
    enable_wandb: bool = False
    wandb_project: str = 'newspace-hybrid-digital-twin'
    wandb_entity: str | None = None


@dataclass(slots=True)
class RunTracker(AbstractContextManager['RunTracker']):
    config: TrackingConfig
    task: str
    params: dict[str, Any]
    run_id: str = field(default_factory=lambda: uuid4().hex)
    run_name: str = field(init=False)
    started_at: str = field(default_factory=utc_now_iso)
    metrics: dict[str, float] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    status: str = 'running'
    ended_at: str | None = None
    _mlflow_run: Any = field(default=None, init=False, repr=False)
    _wandb_run: Any = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.run_name = f'{self.config.run_name_prefix}_{self.task}_{self.run_id[:8]}'
        Path(self.config.artifact_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.registry_path).parent.mkdir(parents=True, exist_ok=True)
        if self.config.enable_mlflow:
            self._start_mlflow()
        if self.config.enable_wandb:
            self._start_wandb()

    def _start_mlflow(self) -> None:
        try:
            import mlflow
        except ImportError:
            return
        if self.config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(self.config.mlflow_tracking_uri)
        mlflow.set_experiment(self.config.experiment_name)
        self._mlflow_run = mlflow.start_run(run_name=self.run_name)
        mlflow.log_params(self.params)

    def _start_wandb(self) -> None:
        try:
            import wandb
        except ImportError:
            return
        self._wandb_run = wandb.init(
            project=self.config.wandb_project,
            entity=self.config.wandb_entity,
            name=self.run_name,
            config=self.params,
            reinit=True,
        )

    def log_metrics(self, metrics: dict[str, float]) -> None:
        self.metrics.update(metrics)
        if self._mlflow_run is not None:
            import mlflow
            mlflow.log_metrics(metrics)
        if self._wandb_run is not None:
            self._wandb_run.log(metrics)

    def log_artifact(self, path: str | Path) -> None:
        p = str(path)
        self.artifacts.append(p)
        if self._mlflow_run is not None:
            import mlflow
            mlflow.log_artifact(p)
        if self._wandb_run is not None and os.path.exists(p):
            self._wandb_run.save(p)

    def set_tags(self, tags: dict[str, str]) -> None:
        self.tags.update(tags)
        if self._mlflow_run is not None:
            import mlflow
            mlflow.set_tags(tags)

    def finalize(self, status: str = 'finished') -> None:
        self.status = status
        self.ended_at = utc_now_iso()
        if self._mlflow_run is not None:
            import mlflow
            mlflow.end_run(status='FINISHED' if status == 'finished' else 'FAILED')
        if self._wandb_run is not None:
            self._wandb_run.finish(exit_code=0 if status == 'finished' else 1)

    def to_record(self) -> dict[str, Any]:
        return {
            'run_id': self.run_id,
            'run_name': self.run_name,
            'experiment_name': self.config.experiment_name,
            'task': self.task,
            'params': self.params,
            'metrics': self.metrics,
            'tags': self.tags,
            'artifacts': self.artifacts,
            'status': self.status,
            'started_at': self.started_at,
            'ended_at': self.ended_at,
        }

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc is not None:
            self.finalize(status='failed')
        elif self.ended_at is None:
            self.finalize(status='finished')
        registry_path = Path(self.config.registry_path)
        with registry_path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(self.to_record()) + '\n')
        return None
