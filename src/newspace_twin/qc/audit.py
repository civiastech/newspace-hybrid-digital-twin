from __future__ import annotations

import csv
import json
from pathlib import Path

import yaml

from newspace_twin.logging.setup import configure_logging
from newspace_twin.registry.repository import read_registry_snapshot
from newspace_twin.settings.config import AppConfig
from newspace_twin.settings.paths import ensure_project_paths
from newspace_twin.validation.crs import validate_crs
from newspace_twin.validation.geometry import validate_vector_files
from newspace_twin.validation.metadata import validate_registry_files
from newspace_twin.validation.timeseries import validate_sensor_csv


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_validation(config: AppConfig) -> dict[str, object]:
    configure_logging(config)
    paths = ensure_project_paths(config)
    manifest_root = Path(paths["manifests"]) / config.active_aoi
    manifest_paths = sorted(manifest_root.glob("*_registry.csv"))
    qc_root = Path(paths["qc"]) / config.active_aoi
    qc_root.mkdir(parents=True, exist_ok=True)

    metadata_report = validate_registry_files(manifest_paths)
    crs_report = validate_crs(manifest_paths, config.runtime.target_crs)

    vector_manifest = manifest_root / "vectors_registry.csv"
    vector_paths = [Path(row["source_uri"]) for row in read_registry_snapshot(vector_manifest)] if vector_manifest.exists() else []
    with open(config.validation_configs["vectors"], "r", encoding="utf-8") as handle:
        vector_rules = yaml.safe_load(handle)
    geometry_report = validate_vector_files(vector_paths, allow_repair=vector_rules["vector_validation"].get("allow_repair", True))

    sensor_manifest = manifest_root / "sensors_registry.csv"
    sensor_paths = [Path(row["source_uri"]) for row in read_registry_snapshot(sensor_manifest)] if sensor_manifest.exists() else []
    with open(config.validation_configs["sensors"], "r", encoding="utf-8") as handle:
        sensor_rules = yaml.safe_load(handle)
    timeseries_report = validate_sensor_csv(sensor_paths, sensor_rules)

    summary = {
        "metadata": {
            "missing_files": metadata_report["missing_files"],
            "missing_checksums": metadata_report["missing_checksums"],
            "duplicate_ids": metadata_report["duplicate_ids"],
        },
        "crs": crs_report,
        "geometry": geometry_report,
        "timeseries": timeseries_report,
    }

    _write_csv(qc_root / "registry_validation.csv", metadata_report["findings"])
    with (qc_root / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    return {
        "qc_root": str(qc_root),
        "summary_path": str(qc_root / "summary.json"),
        "manifest_count": len(manifest_paths),
    }
