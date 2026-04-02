from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio


def _read_stack(path: str | Path) -> tuple[np.ndarray, dict]:
    path = Path(path)
    with rasterio.open(path) as src:
        data = src.read().astype(np.float32)
        meta = src.meta.copy()
    return data, meta


def _write_single_band(path: str | Path, array: np.ndarray, meta: dict) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    out_meta = meta.copy()
    out_meta.update(count=1, dtype="float32")

    with rasterio.open(path, "w", **out_meta) as dst:
        dst.write(array.astype(np.float32), 1)

    return path


def compute_ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    return (nir - red) / (nir + red + 1e-6)


def compute_nbr(nir: np.ndarray, swir2: np.ndarray) -> np.ndarray:
    return (nir - swir2) / (nir + swir2 + 1e-6)


def build_optical_wildfire_features(
    pre_stack_path: str | Path,
    post_stack_path: str | Path,
    out_dir: str | Path,
) -> dict[str, str]:
    """
    Expected band order in stack:
    1. B02
    2. B03
    3. B04
    4. B08
    5. B11
    6. B12
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    pre, meta = _read_stack(pre_stack_path)
    post, _ = _read_stack(post_stack_path)

    if pre.shape[0] < 6 or post.shape[0] < 6:
        raise ValueError("Expected 6-band Sentinel-2 stacks with B02,B03,B04,B08,B11,B12.")

    red_pre = pre[2]
    nir_pre = pre[3]
    swir2_pre = pre[5]

    red_post = post[2]
    nir_post = post[3]
    swir2_post = post[5]

    ndvi_pre = compute_ndvi(nir_pre, red_pre)
    ndvi_post = compute_ndvi(nir_post, red_post)

    nbr_pre = compute_nbr(nir_pre, swir2_pre)
    nbr_post = compute_nbr(nir_post, swir2_post)

    dnbr = nbr_pre - nbr_post

    outputs = {
        "ndvi_pre": str(_write_single_band(out_dir / "ndvi_pre.tif", ndvi_pre, meta)),
        "ndvi_post": str(_write_single_band(out_dir / "ndvi_post.tif", ndvi_post, meta)),
        "nbr_pre": str(_write_single_band(out_dir / "nbr_pre.tif", nbr_pre, meta)),
        "nbr_post": str(_write_single_band(out_dir / "nbr_post.tif", nbr_post, meta)),
        "dnbr": str(_write_single_band(out_dir / "dnbr.tif", dnbr, meta)),
    }

    return outputs