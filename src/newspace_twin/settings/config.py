from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class PathsConfig:
    project_root: str
    data_raw: str
    data_interim: str
    data_processed: str
    data_manifests: str
    data_features: str
    data_predictions: str
    data_twin: str
    reports: str
    qc: str


@dataclass(slots=True)
class DatabaseConfig:
    host: str
    port: int
    dbname: str
    user: str
    password: str


@dataclass(slots=True)
class LoggingConfig:
    level: str
    log_dir: str


@dataclass(slots=True)
class RuntimeConfig:
    random_seed: int
    target_crs: int
    timezone: str


@dataclass(slots=True)
class ProjectConfig:
    name: str
    run_name: str


@dataclass(slots=True)
class AppConfig:
    project: ProjectConfig
    paths: PathsConfig
    database: DatabaseConfig
    logging: LoggingConfig
    runtime: RuntimeConfig
    active_aoi: str
    active_experiment: str
    ingestion_configs: dict[str, str]
    validation_configs: dict[str, str]


def read_yaml(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_config(path: str | Path) -> AppConfig:
    raw = read_yaml(path)
    return AppConfig(
        project=ProjectConfig(**raw["project"]),
        paths=PathsConfig(**raw["paths"]),
        database=DatabaseConfig(**raw["database"]),
        logging=LoggingConfig(**raw["logging"]),
        runtime=RuntimeConfig(**raw["runtime"]),
        active_aoi=raw["active_aoi"],
        active_experiment=raw["active_experiment"],
        ingestion_configs=raw.get("ingestion_configs", {}),
        validation_configs=raw.get("validation_configs", {}),
    )
