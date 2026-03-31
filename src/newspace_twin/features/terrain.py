from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import rasterio


@dataclass(slots=True)
class TerrainFeatureResult:
    source_uri: str
    output_uri: str
    band_names: list[str]


def build_terrain_features(source_path: str | Path, output_path: str | Path) -> TerrainFeatureResult:
    """Minimal terrain hook preserving DEM and first-order slope proxy."""
    src_path = Path(source_path)
    dst_path = Path(output_path)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(src_path) as src:
        dem = src.read(1).astype(np.float32)
        gy, gx = np.gradient(dem)
        slope = np.hypot(gx, gy).astype(np.float32)
        meta = src.meta.copy()
        meta.update(count=2, dtype='float32')
        with rasterio.open(dst_path, 'w', **meta) as dst:
            dst.write(dem, 1)
            dst.write(slope, 2)
            dst.set_band_description(1, 'DEM')
            dst.set_band_description(2, 'SLOPE_PROXY')
    return TerrainFeatureResult(source_uri=str(src_path), output_uri=str(dst_path), band_names=['DEM', 'SLOPE_PROXY'])
