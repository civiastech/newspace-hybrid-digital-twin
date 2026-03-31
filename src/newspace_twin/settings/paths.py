from __future__ import annotations

from pathlib import Path

from newspace_twin.settings.config import AppConfig


def ensure_project_paths(config: AppConfig) -> dict[str, Path]:
    base = Path(config.paths.project_root)
    path_map = {
        "raw": base / config.paths.data_raw,
        "interim": base / config.paths.data_interim,
        "processed": base / config.paths.data_processed,
        "manifests": base / config.paths.data_manifests,
        "features": base / config.paths.data_features,
        "predictions": base / config.paths.data_predictions,
        "twin": base / config.paths.data_twin,
        "reports": base / config.paths.reports,
        "qc": base / config.paths.qc,
    }
    for path in path_map.values():
        path.mkdir(parents=True, exist_ok=True)
    return path_map
