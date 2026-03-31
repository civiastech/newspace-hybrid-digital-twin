from __future__ import annotations

from pathlib import Path

import geopandas as gpd

from newspace_twin.ingestion.base import BaseIngestor, IngestionResult
from newspace_twin.ingestion.utils import find_matching_files
from newspace_twin.registry.checksum import sha256_file
from newspace_twin.registry.models import RegistryRecord
from newspace_twin.registry.repository import write_registry_snapshot


class VectorIngestor(BaseIngestor):
    def ingest(self) -> IngestionResult:
        files = find_matching_files(self.raw_dir, self.modality_config["file_globs"])
        records: list[RegistryRecord] = []
        for path in files:
            gdf = gpd.read_file(path)
            crs_epsg = gdf.crs.to_epsg() if gdf.crs is not None else None
            footprint = gdf.total_bounds.tolist() if not gdf.empty else None
            metadata = {"rows": int(len(gdf)), "columns": list(gdf.columns)}
            records.append(
                RegistryRecord(
                    dataset_id=path.stem,
                    modality="vectors",
                    source_uri=str(path),
                    checksum=sha256_file(path),
                    aoi_id=self.aoi_id,
                    crs_epsg=crs_epsg,
                    metadata=metadata,
                    footprint_wkt=str(footprint),
                )
            )
        manifest_path = Path(self.paths["manifests"]) / self.aoi_id / "vectors_registry.csv"
        write_registry_snapshot(records, manifest_path)
        warnings = ["No vector files found."] if not files else []
        return IngestionResult("vectors", len(records), str(manifest_path), warnings)
