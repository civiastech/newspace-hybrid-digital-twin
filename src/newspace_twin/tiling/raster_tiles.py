from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds


@dataclass(slots=True)
class TileBuildResult:
    manifest_uri: str
    tile_count: int
    tile_root: str


def tile_feature_raster(
    raster_path: str | Path,
    grid_path: str | Path,
    output_root: str | Path,
    *,
    prefix: str,
) -> TileBuildResult:
    grid = gpd.read_file(grid_path)
    raster_p = Path(raster_path)
    tile_root = Path(output_root)
    tile_root.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []

    with rasterio.open(raster_p) as src:
        working_grid = grid.to_crs(src.crs) if grid.crs != src.crs else grid

        for _, rec in working_grid.iterrows():
            minx, miny, maxx, maxy = rec.geometry.bounds
            window = from_bounds(minx, miny, maxx, maxy, transform=src.transform)
            window = window.round_offsets().round_lengths()

            # enforce minimum 1x1 tile
            if window.width < 1:
                window = window.round_offsets()
                window = rasterio.windows.Window(window.col_off, window.row_off, 1, max(1, window.height))
            if window.height < 1:
                window = window.round_offsets()
                window = rasterio.windows.Window(window.col_off, window.row_off, max(1, window.width), 1)

            data = src.read(window=window, boundless=True, fill_value=0)

            if data.size == 0:
                continue

            tile_path = tile_root / f"{prefix}_{rec['unit_id']}.npy"
            np.save(tile_path, data.astype(np.float32))

            rows.append(
                {
                    "unit_id": rec["unit_id"],
                    "tile_uri": str(tile_path),
                    "source_raster": str(raster_p),
                    "height": int(data.shape[1]),
                    "width": int(data.shape[2]),
                    "bands": int(data.shape[0]),
                }
            )

    manifest_path = tile_root / f"{prefix}_tiles.csv"
    pd.DataFrame(rows).to_csv(manifest_path, index=False)

    return TileBuildResult(
        manifest_uri=str(manifest_path),
        tile_count=len(rows),
        tile_root=str(tile_root),
    )