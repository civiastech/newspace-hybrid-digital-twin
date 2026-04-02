from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import yaml

from newspace_twin.ingestion.stac_client import STACClient
from newspace_twin.preprocessing.stack_bands import build_median_composite, describe_raster


def load_aoi_config(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    config_path = Path("configs/aois/wildfire_case_aoi_real.yaml")
    cfg = load_aoi_config(config_path)

    aoi_path = Path(cfg["geometry_file"])
    aoi = gpd.read_file(aoi_path)

    client = STACClient()

    pre_items = client.filter_sentinel2(
        aoi_gdf=aoi,
        start_date=cfg["time_windows"]["pre_start"],
        end_date=cfg["time_windows"]["pre_end"],
        cloud_cover_max=cfg.get("filters", {}).get("sentinel2_cloud_cover_lt", 20),
        max_items=cfg.get("filters", {}).get("max_items_per_window", 6),
    )

    post_items = client.filter_sentinel2(
        aoi_gdf=aoi,
        start_date=cfg["time_windows"]["post_start"],
        end_date=cfg["time_windows"]["post_end"],
        cloud_cover_max=cfg.get("filters", {}).get("sentinel2_cloud_cover_lt", 20),
        max_items=cfg.get("filters", {}).get("max_items_per_window", 6),
    )

    out_dir = Path("data/interim") / cfg["aoi_id"]
    pre_path = out_dir / "s2_pre.tif"
    post_path = out_dir / "s2_post.tif"

    build_median_composite(
        pre_items,
        pre_path,
        epsg=int(str(cfg["target_crs"]).split(":")[-1]),
        resolution=10.0,
    )
    build_median_composite(
        post_items,
        post_path,
        epsg=int(str(cfg["target_crs"]).split(":")[-1]),
        resolution=10.0,
    )

    print("Pre composite:", describe_raster(pre_path))
    print("Post composite:", describe_raster(post_path))


if __name__ == "__main__":
    main()