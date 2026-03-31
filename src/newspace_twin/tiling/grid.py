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


def build_analysis_grid(aoi_path: str | Path, output_path: str | Path, *, cell_size: float) -> GridBuildResult:
    """Build a regular grid intersecting the AOI."""
    src_path = Path(aoi_path)
    dst_path = Path(output_path)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    aoi = gpd.read_file(src_path)
    if aoi.empty:
        raise ValueError(f'Empty AOI file: {src_path}')
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
            if not clipped.is_empty:
                cells.append(clipped)
                ids.append(f'unit_{idx:05d}')
                idx += 1
            y += cell_size
        x += cell_size

    grid = gpd.GeoDataFrame({'unit_id': ids}, geometry=cells, crs=aoi.crs)
    grid.to_file(dst_path, driver='GeoJSON')
    return GridBuildResult(output_uri=str(dst_path), unit_count=int(len(grid)), cell_size=float(cell_size))
