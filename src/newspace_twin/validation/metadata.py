from __future__ import annotations

from pathlib import Path

from newspace_twin.registry.repository import read_registry_snapshot


def validate_registry_files(manifest_paths: list[Path]) -> dict[str, object]:
    findings: list[dict[str, str]] = []
    missing_files = 0
    missing_checksums = 0
    duplicate_ids: set[str] = set()
    seen_ids: set[str] = set()

    for manifest in manifest_paths:
        for row in read_registry_snapshot(manifest):
            dataset_id = row["dataset_id"]
            source_uri = row["source_uri"]
            checksum = row["checksum"]
            exists = Path(source_uri).exists()
            if not exists:
                missing_files += 1
            if not checksum:
                missing_checksums += 1
            if dataset_id in seen_ids:
                duplicate_ids.add(dataset_id)
            seen_ids.add(dataset_id)
            findings.append(
                {
                    "dataset_id": dataset_id,
                    "modality": row["modality"],
                    "source_uri": source_uri,
                    "file_exists": str(exists),
                    "has_checksum": str(bool(checksum)),
                }
            )
    return {
        "findings": findings,
        "missing_files": missing_files,
        "missing_checksums": missing_checksums,
        "duplicate_ids": sorted(duplicate_ids),
    }
