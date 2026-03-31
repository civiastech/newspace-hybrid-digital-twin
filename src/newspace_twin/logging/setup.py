from __future__ import annotations

import logging
from pathlib import Path

from newspace_twin.settings.config import AppConfig

logger = logging.getLogger("newspace_twin")


def configure_logging(config: AppConfig) -> None:
    log_dir = Path(config.paths.project_root) / config.logging.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{config.project.run_name}.log"

    if logger.handlers:
        return

    logger.setLevel(getattr(logging, config.logging.level.upper(), logging.INFO))
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
