from pathlib import Path

from newspace_twin.settings.config import load_config


def test_load_config() -> None:
    config = load_config(Path("configs/base.yaml"))
    assert config.active_aoi == "wildfire_case_aoi"
    assert "sentinel1" in config.ingestion_configs
