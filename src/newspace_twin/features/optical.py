from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import rasterio


@dataclass(slots=True)
class OpticalFeatureResult:
    source_uri: str
    output_uri: str
    band_names: list[str]
    width: int
    height: int


def _safe_index(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    out = np.zeros_like(numerator, dtype=np.float32)
    np.divide(numerator, denominator, out=out, where=np.abs(denominator) > 1e-6)
    return np.clip(out, -1.0, 1.0).astype(np.float32)


def build_optical_features(
    source_path: str | Path,
    output_path: str | Path,
    *,
    band_map: dict[str, int] | None = None,
) -> OpticalFeatureResult:
    """Build NDVI, NBR, and NDWI from a Sentinel-2 style multiband raster.

    Assumes 1-based band indexing. If no band_map is provided, a 6-band stack is
    assumed in this order: B02, B03, B04, B08, B11, B12.
    """
    default_map = {'B02': 1, 'B03': 2, 'B04': 3, 'B08': 4, 'B11': 5, 'B12': 6}
    bands = band_map or default_map

    src_path = Path(source_path)
    dst_path = Path(output_path)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(src_path) as src:
        red = src.read(bands['B04']).astype(np.float32)
        nir = src.read(bands['B08']).astype(np.float32)
        green = src.read(bands['B03']).astype(np.float32)
        swir2 = src.read(bands['B12']).astype(np.float32)

        ndvi = _safe_index(nir - red, nir + red)
        nbr = _safe_index(nir - swir2, nir + swir2)
        ndwi = _safe_index(green - nir, green + nir)

        meta = src.meta.copy()
        meta.update(count=3, dtype='float32')
        with rasterio.open(dst_path, 'w', **meta) as dst:
            dst.write(ndvi, 1)
            dst.write(nbr, 2)
            dst.write(ndwi, 3)
            dst.set_band_description(1, 'NDVI')
            dst.set_band_description(2, 'NBR')
            dst.set_band_description(3, 'NDWI')

        return OpticalFeatureResult(
            source_uri=str(src_path),
            output_uri=str(dst_path),
            band_names=['NDVI', 'NBR', 'NDWI'],
            width=src.width,
            height=src.height,
        )
