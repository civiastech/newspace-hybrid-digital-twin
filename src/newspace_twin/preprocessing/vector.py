from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd


@dataclass(slots=True)
class VectorPreprocessResult:
    source_uri: str
    output_uri: str
    feature_count: int
    crs_epsg: int | None
    repaired_features: int


def preprocess_vector(
    source_path: str | Path,
    output_path: str | Path,
    *,
    target_epsg: int,
    allow_repair: bool = True,
) -> VectorPreprocessResult:
    src_path = Path(source_path)
    dst_path = Path(output_path)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    gdf = gpd.read_file(src_path)
    repaired = 0
    invalid_before = (~gdf.geometry.is_valid).sum() if not gdf.empty else 0
    if invalid_before and allow_repair:
        gdf['geometry'] = gdf.buffer(0)
        repaired = int(invalid_before - (~gdf.geometry.is_valid).sum())

    if gdf.crs is None:
        raise ValueError(f'Input vector has no CRS: {src_path}')
    if gdf.crs.to_epsg() != target_epsg:
        gdf = gdf.to_crs(epsg=target_epsg)

    normalized = gdf.copy()
    normalized.columns = [str(col).strip().lower().replace(' ', '_') for col in normalized.columns]
    normalized.to_file(dst_path, driver='GeoJSON')

    return VectorPreprocessResult(
        source_uri=str(src_path),
        output_uri=str(dst_path),
        feature_count=int(len(normalized)),
        crs_epsg=normalized.crs.to_epsg() if normalized.crs is not None else None,
        repaired_features=repaired,
    )
