from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import geopandas as gpd
import yaml


@dataclass(slots=True)
class AOIContract:
    aoi_id: str
    name: str
    geometry_wkt: str
    crs_epsg: int
    time_start: str | None
    time_end: str | None
    case_study_type: str
    geometry_file: str | None = None


def load_aoi_contract(config_path: str | Path, project_root: str | Path = '.') -> AOIContract:
    with open(config_path, 'r', encoding='utf-8') as handle:
        raw: dict[str, Any] = yaml.safe_load(handle)
    geometry_file = raw.get('geometry_file')
    geometry_wkt = 'GEOMETRYCOLLECTION EMPTY'
    crs_epsg = int(raw.get('target_crs', 4326))
    if geometry_file:
        geom_path = Path(project_root) / geometry_file
        if geom_path.exists():
            gdf = gpd.read_file(geom_path)
            if gdf.crs is not None and gdf.crs.to_epsg() is not None:
                crs_epsg = int(gdf.crs.to_epsg())
            geometry_wkt = gdf.geometry.union_all().wkt if not gdf.empty else geometry_wkt
    return AOIContract(
        aoi_id=raw['aoi_id'],
        name=raw['name'],
        geometry_wkt=geometry_wkt,
        crs_epsg=crs_epsg,
        time_start=raw.get('time_start'),
        time_end=raw.get('time_end'),
        case_study_type=raw['case_study_type'],
        geometry_file=geometry_file,
    )
