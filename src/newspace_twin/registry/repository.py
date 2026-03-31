from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from newspace_twin.registry.models import RegistryRecord


CSV_FIELDS = [
    "dataset_id",
    "modality",
    "source_uri",
    "checksum",
    "aoi_id",
    "crs_epsg",
    "acquired_at",
    "ingested_at",
    "lineage_parent_id",
    "status",
    "metadata",
    "footprint_wkt",
]


def write_registry_snapshot(records: Iterable[RegistryRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for record in records:
            row = asdict(record)
            row["metadata"] = json.dumps(row["metadata"], ensure_ascii=False, sort_keys=True)
            writer.writerow(row)


def read_registry_snapshot(input_path: Path) -> list[dict[str, str]]:
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))
