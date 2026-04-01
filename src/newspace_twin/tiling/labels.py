from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
from rasterio.transform import from_bounds


def _max_class(values: np.ndarray) -> int:
    values = values.astype(np.int64).ravel()
    values = values[values >= 0]
    if values.size == 0:
        return 0
    return int(values.max())


def build_tile_labels_from_severity_mask(
    grid_path: str | Path,
    mask_path: str | Path,
    aoi_geojson_path: str | Path,
) -> dict[str, int]:
    grid = gpd.read_file(grid_path)
    aoi = gpd.read_file(aoi_geojson_path)

    if grid.empty:
        return {}

    if aoi.empty:
        raise ValueError(f"AOI is empty: {aoi_geojson_path}")

    if aoi.crs is None:
        raise ValueError(f"AOI has no CRS: {aoi_geojson_path}")

    if grid.crs is None:
        raise ValueError(f"Grid has no CRS: {grid_path}")

    if aoi.crs.to_epsg() != 4326:
        aoi = aoi.to_crs(epsg=4326)

    if grid.crs.to_epsg() != 4326:
        grid = grid.to_crs(epsg=4326)

    mask = np.load(mask_path)
    if mask.ndim != 2:
        raise ValueError("Severity mask must be 2D")

    minx, miny, maxx, maxy = aoi.total_bounds
    height, width = mask.shape
    transform = from_bounds(minx, miny, maxx, maxy, width=width, height=height)

    labels: dict[str, int] = {}

    for _, rec in grid.iterrows():
        unit_id = rec["unit_id"]
        geom = rec.geometry
        bx_min, by_min, bx_max, by_max = geom.bounds

        col0, row1 = ~transform * (bx_min, by_min)
        col1, row0 = ~transform * (bx_max, by_max)

        c0 = max(0, int(np.floor(min(col0, col1))))
        c1 = min(width, int(np.ceil(max(col0, col1))))
        r0 = max(0, int(np.floor(min(row0, row1))))
        r1 = min(height, int(np.ceil(max(row0, row1))))

        if c1 <= c0 or r1 <= r0:
            labels[unit_id] = 0
            continue

        tile_mask = mask[r0:r1, c0:c1]
        labels[unit_id] = _max_class(tile_mask)

    return labels
