from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.warp import Resampling, calculate_default_transform, reproject


@dataclass(slots=True)
class RasterPreprocessResult:
    source_uri: str
    output_uri: str
    crs_epsg: int | None
    width: int
    height: int
    was_clipped: bool
    was_reprojected: bool


_RESAMPLING_MAP: dict[str, Resampling] = {
    "nearest": Resampling.nearest,
    "bilinear": Resampling.bilinear,
    "cubic": Resampling.cubic,
}


def _load_aoi_shapes(aoi_path: str | Path | None, target_epsg: int) -> list[dict[str, Any]] | None:
    if aoi_path is None:
        return None
    path = Path(aoi_path)
    if not path.exists():
        return None
    gdf = gpd.read_file(path)
    if gdf.empty:
        return None
    if gdf.crs is None:
        raise ValueError(f"AOI file has no CRS: {path}")
    if gdf.crs.to_epsg() != target_epsg:
        gdf = gdf.to_crs(epsg=target_epsg)
    return [geom.__geo_interface__ for geom in gdf.geometry if geom is not None]


def preprocess_raster(
    source_path: str | Path,
    output_path: str | Path,
    *,
    target_epsg: int,
    aoi_path: str | Path | None,
    clip_to_aoi: bool,
    resampling: str = "bilinear",
) -> RasterPreprocessResult:
    src_path = Path(source_path)
    dst_path = Path(output_path)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    suffix = src_path.suffix.lower()

    # Synthetic NPZ support
    if suffix == ".npz":
        data = np.load(src_path)
        arrays = {k: data[k] for k in data.files}
        np.savez_compressed(dst_path, **arrays)

        first_key = list(data.files)[0]
        arr = data[first_key]

        if arr.ndim == 2:
            height, width = arr.shape
        elif arr.ndim >= 3:
            height, width = arr.shape[-2], arr.shape[-1]
        else:
            height = 1
            width = int(arr.shape[0]) if arr.ndim == 1 else 1

        return RasterPreprocessResult(
            source_uri=str(src_path),
            output_uri=str(dst_path),
            crs_epsg=4326,
            width=width,
            height=height,
            was_clipped=False,
            was_reprojected=False,
        )

    with rasterio.open(src_path) as src:
        source_epsg = src.crs.to_epsg() if src.crs is not None else None
        target_crs = f"EPSG:{target_epsg}"
        was_reprojected = source_epsg != target_epsg
        resampling_enum = _RESAMPLING_MAP.get(resampling, Resampling.bilinear)

        if was_reprojected:
            transform, width, height = calculate_default_transform(
                src.crs,
                target_crs,
                src.width,
                src.height,
                *src.bounds,
            )
            meta = src.meta.copy()
            meta.update({"crs": target_crs, "transform": transform, "width": width, "height": height})
            temp_path = dst_path.with_suffix(".tmp.tif")
            with rasterio.open(temp_path, "w", **meta) as dst:
                for band in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, band),
                        destination=rasterio.band(dst, band),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=target_crs,
                        resampling=resampling_enum,
                    )
            working_path = temp_path
        else:
            working_path = src_path

    was_clipped = False
    shapes = _load_aoi_shapes(aoi_path, target_epsg) if clip_to_aoi else None

    with rasterio.open(working_path) as work_src:
        if shapes:
            clipped_data, clipped_transform = mask(work_src, shapes=shapes, crop=True)
            meta = work_src.meta.copy()
            meta.update(
                {
                    "height": clipped_data.shape[1],
                    "width": clipped_data.shape[2],
                    "transform": clipped_transform,
                }
            )
            with rasterio.open(dst_path, "w", **meta) as dst:
                dst.write(clipped_data)
            was_clipped = True
        else:
            if working_path != dst_path:
                dst_path.write_bytes(Path(working_path).read_bytes())

        width = work_src.width if not was_clipped else clipped_data.shape[2]
        height = work_src.height if not was_clipped else clipped_data.shape[1]
        crs_epsg = work_src.crs.to_epsg() if work_src.crs is not None else target_epsg

    temp_path = dst_path.with_suffix(".tmp.tif")
    if temp_path.exists():
        temp_path.unlink()

    return RasterPreprocessResult(
        source_uri=str(src_path),
        output_uri=str(dst_path),
        crs_epsg=crs_epsg,
        width=width,
        height=height,
        was_clipped=was_clipped,
        was_reprojected=was_reprojected,
    )