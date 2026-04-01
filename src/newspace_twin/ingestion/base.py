from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from newspace_twin.logging.setup import configure_logging, logger
from newspace_twin.settings.config import AppConfig
from newspace_twin.settings.paths import ensure_project_paths


@dataclass(slots=True)
class IngestionResult:
    modality: str
    records_written: int
    manifest_path: str
    warnings: list[str]


class BaseIngestor(ABC):
    def __init__(self, config: AppConfig, modality_config_path: str) -> None:
        self.config = config
        self.modality_config_path = modality_config_path
        with open(modality_config_path, encoding="utf-8") as handle:
            self.modality_config: dict[str, Any] = yaml.safe_load(handle)
        self.paths = ensure_project_paths(config)

    @property
    def aoi_id(self) -> str:
        return self.config.active_aoi

    @property
    def raw_dir(self) -> Path:
        relative = self.modality_config["relative_raw_dir"].format(aoi_id=self.aoi_id)
        return Path(self.config.paths.project_root) / relative

    @abstractmethod
    def ingest(self) -> IngestionResult:
        raise NotImplementedError


def run_ingestion(config: AppConfig) -> dict[str, object]:
    configure_logging(config)
    manifests_dir = ensure_project_paths(config)["manifests"] / config.active_aoi
    manifests_dir.mkdir(parents=True, exist_ok=True)

    from newspace_twin.ingestion.sensors import SensorIngestor
    from newspace_twin.ingestion.sentinel1 import Sentinel1Ingestor
    from newspace_twin.ingestion.sentinel2 import Sentinel2Ingestor
    from newspace_twin.ingestion.uav import UAVIngestor
    from newspace_twin.ingestion.vectors import VectorIngestor

    ingestors: dict[str, type[BaseIngestor]] = {
        "sentinel1": Sentinel1Ingestor,
        "sentinel2": Sentinel2Ingestor,
        "uav": UAVIngestor,
        "sensors": SensorIngestor,
        "vectors": VectorIngestor,
    }

    results: list[IngestionResult] = []
    total_records = 0
    manifest_map: dict[str, str] = {}

    for modality, cls in ingestors.items():
        config_path = config.ingestion_configs[modality]
        ingestor = cls(config, config_path)
        result = ingestor.ingest()
        results.append(result)
        total_records += result.records_written
        manifest_map[modality] = result.manifest_path
        logger.info("Ingested %s records for %s", result.records_written, modality)

    return {
        "total_records_written": total_records,
        "modality_manifests": manifest_map,
        "warnings": {result.modality: result.warnings for result in results if result.warnings},
    }
