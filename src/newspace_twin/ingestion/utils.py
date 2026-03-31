from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
import rasterio
from shapely.geometry import box

from newspace_twin.registry.checksum import sha256_file
from newspace_twin.registry.models import RegistryRecord


def find_matching_files(root_dir: Path, file_globs: Iterable[str]) -> list[Path]:
    files: list[Path] = []
    if not root_dir.exists():
        return []
    for pattern in file_globs:
        files.extend(root_dir.rglob(pattern))
    return sorted({path.resolve() for path in files})


def build_raster_record(file_path: Path, modality: str, aoi_id: str) -> RegistryRecord:
    with rasterio.open(file_path) as src:
        bounds = src.bounds
        footprint = box(bounds.left, bounds.bottom, bounds.right, bounds.top).wkt
        crs_epsg = src.crs.to_epsg() if src.crs is not None else None
        metadata = {
            "width": src.width,
            "height": src.height,
            "count": src.count,
            "dtype": src.dtypes[0] if src.dtypes else None,
            "driver": src.driver,
            "transform": tuple(src.transform),
        }
    return RegistryRecord(
        dataset_id=file_path.stem,
        modality=modality,
        source_uri=str(file_path),
        checksum=sha256_file(file_path),
        aoi_id=aoi_id,
        crs_epsg=crs_epsg,
        metadata=metadata,
        footprint_wkt=footprint,
    )


def build_csv_record(file_path: Path, modality: str, aoi_id: str) -> RegistryRecord:
    frame = pd.read_csv(file_path)
    metadata = {
        "rows": int(len(frame)),
        "columns": list(frame.columns),
    }
    acquired_at = None
    if "timestamp" in frame.columns and not frame.empty:
        timestamps = pd.to_datetime(frame["timestamp"], errors="coerce", utc=True)
        if timestamps.notna().any():
            acquired_at = timestamps.min().to_pydatetime()
    return RegistryRecord(
        dataset_id=file_path.stem,
        modality=modality,
        source_uri=str(file_path),
        checksum=sha256_file(file_path),
        aoi_id=aoi_id,
        acquired_at=acquired_at,
        metadata=metadata,
    )
