from __future__ import annotations

from pathlib import Path

from newspace_twin.registry.repository import read_registry_snapshot


RASTER_MODALITIES = {"sentinel1", "sentinel2", "uav", "vectors"}


def validate_crs(manifest_paths: list[Path], target_crs: int) -> dict[str, object]:
    missing_crs: list[str] = []
    mismatched_crs: list[dict[str, str]] = []

    for manifest in manifest_paths:
        for row in read_registry_snapshot(manifest):
            if row["modality"] not in RASTER_MODALITIES:
                continue
            crs_value = row.get("crs_epsg")
            if crs_value in {None, "", "None"}:
                missing_crs.append(row["source_uri"])
                continue
            if int(crs_value) != int(target_crs):
                mismatched_crs.append(
                    {
                        "source_uri": row["source_uri"],
                        "crs_epsg": crs_value,
                        "target_crs": str(target_crs),
                    }
                )

    return {
        "missing_crs": missing_crs,
        "mismatched_crs": mismatched_crs,
    }
