from __future__ import annotations

from pathlib import Path

import geopandas as gpd


def validate_vector_files(vector_paths: list[Path], allow_repair: bool = True) -> dict[str, object]:
    invalid_geometries: list[str] = []
    repaired_files: list[str] = []
    empty_files: list[str] = []

    for path in vector_paths:
        gdf = gpd.read_file(path)
        if gdf.empty:
            empty_files.append(str(path))
            continue
        if not gdf.is_valid.all():
            invalid_geometries.append(str(path))
            if allow_repair:
                repaired = gdf.copy()
                repaired["geometry"] = repaired.buffer(0)
                if repaired.is_valid.all():
                    repaired_files.append(str(path))

    return {
        "invalid_geometries": invalid_geometries,
        "repaired_files": repaired_files,
        "empty_files": empty_files,
    }
