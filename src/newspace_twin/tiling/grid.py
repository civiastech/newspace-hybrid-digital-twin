from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
from shapely.geometry import box


@dataclass(slots=True)
class GridBuildResult:
    output_uri: str
    unit_count: int
    cell_size: float


def build_analysis_grid(
    aoi_path: str | Path,
    output_path: str | Path,
    *,
    cell_size: float,
    target_epsg: int = 3763,
) -> GridBuildResult:
    """Build a regular grid in meters by projecting the AOI to a metric CRS first."""
    src_path = Path(aoi_path)
    dst_path = Path(output_path)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    aoi = gpd.read_file(src_path)
    if aoi.empty:
        raise ValueError(f"Empty AOI file: {src_path}")
    if aoi.crs is None:
        raise ValueError(f"AOI has no CRS: {src_path}")

    # Reproject to metric CRS so cell_size is interpreted in meters
    if aoi.crs.to_epsg() != target_epsg:
        aoi = aoi.to_crs(epsg=target_epsg)

    union = aoi.geometry.union_all()
    minx, miny, maxx, maxy = union.bounds

    cells = []
    ids = []
    idx = 0

    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            cell = box(x, y, min(x + cell_size, maxx), min(y + cell_size, maxy))
            clipped = cell.intersection(union)
            if not clipped.is_empty and clipped.area > 0:
                cells.append(clipped)
                ids.append(f"unit_{idx:05d}")
                idx += 1
            y += cell_size
        x += cell_size

    if not cells:
        raise ValueError("No grid cells were created from the AOI.")

    grid = gpd.GeoDataFrame({"unit_id": ids}, geometry=cells, crs=f"EPSG:{target_epsg}")

    # Save as WGS84 GeoJSON for compatibility
    grid = grid.to_crs(epsg=4326)
    grid.to_file(dst_path, driver="GeoJSON")

    return GridBuildResult(
        output_uri=str(dst_path),
        unit_count=int(len(grid)),
        cell_size=float(cell_size),
    )
