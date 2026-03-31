from __future__ import annotations

from pathlib import Path

from newspace_twin.ingestion.base import BaseIngestor, IngestionResult
from newspace_twin.ingestion.utils import build_csv_record, find_matching_files
from newspace_twin.registry.repository import write_registry_snapshot


class SensorIngestor(BaseIngestor):
    def ingest(self) -> IngestionResult:
        files = find_matching_files(self.raw_dir, self.modality_config["file_globs"])
        records = [build_csv_record(path, "sensors", self.aoi_id) for path in files]
        manifest_path = Path(self.paths["manifests"]) / self.aoi_id / "sensors_registry.csv"
        write_registry_snapshot(records, manifest_path)
        warnings = ["No sensor CSV files found."] if not files else []
        return IngestionResult("sensors", len(records), str(manifest_path), warnings)
