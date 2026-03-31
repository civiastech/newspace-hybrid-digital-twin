from __future__ import annotations

from pathlib import Path

from newspace_twin.ingestion.base import BaseIngestor, IngestionResult
from newspace_twin.ingestion.utils import build_raster_record, find_matching_files
from newspace_twin.registry.repository import write_registry_snapshot


class Sentinel2Ingestor(BaseIngestor):
    def ingest(self) -> IngestionResult:
        files = find_matching_files(self.raw_dir, self.modality_config["file_globs"])
        records = [build_raster_record(path, "sentinel2", self.aoi_id) for path in files]
        manifest_path = Path(self.paths["manifests"]) / self.aoi_id / "sentinel2_registry.csv"
        write_registry_snapshot(records, manifest_path)
        warnings = ["No Sentinel-2 files found."] if not files else []
        return IngestionResult("sentinel2", len(records), str(manifest_path), warnings)
