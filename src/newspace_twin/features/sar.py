from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import rasterio


@dataclass(slots=True)
class SarFeatureResult:
    source_uri: str
    output_uri: str
    band_names: list[str]
    width: int
    height: int


def _safe_ratio(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    out = np.zeros_like(a, dtype=np.float32)
    np.divide(a, b, out=out, where=np.abs(b) > 1e-6)
    return out.astype(np.float32)


def build_sar_features(source_path: str | Path, output_path: str | Path) -> SarFeatureResult:
    """Build SAR feature layers from a 2-band Sentinel-1 style raster.

    Expected band order: VV, VH.
    Outputs: VV, VH, VV/VH ratio, VV-VH difference.
    """
    src_path = Path(source_path)
    dst_path = Path(output_path)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(src_path) as src:
        vv = src.read(1).astype(np.float32)
        vh = src.read(2).astype(np.float32) if src.count >= 2 else np.zeros_like(vv)
        ratio = _safe_ratio(vv, vh)
        diff = (vv - vh).astype(np.float32)

        meta = src.meta.copy()
        meta.update(count=4, dtype='float32')
        with rasterio.open(dst_path, 'w', **meta) as dst:
            dst.write(vv, 1)
            dst.write(vh, 2)
            dst.write(ratio, 3)
            dst.write(diff, 4)
            for i, name in enumerate(['VV', 'VH', 'VV_VH_RATIO', 'VV_MINUS_VH'], start=1):
                dst.set_band_description(i, name)

        return SarFeatureResult(
            source_uri=str(src_path),
            output_uri=str(dst_path),
            band_names=['VV', 'VH', 'VV_VH_RATIO', 'VV_MINUS_VH'],
            width=src.width,
            height=src.height,
        )
