from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import rasterio
import xarray as xr
import rioxarray
import stackstac

try:
    import planetary_computer
except ImportError:  # optional if provider does not require signing
    planetary_computer = None


S2_BANDS = ["B02", "B03", "B04", "B08", "B11", "B12"]


def sign_items(items: Iterable):
    items = list(items)
    if planetary_computer is None:
        return items
    return [planetary_computer.sign(item) for item in items]


def build_median_composite(
    items: Iterable,
    out_path: str | Path,
    epsg: int = 3763,
    resolution: float = 10.0,
    bands: list[str] | None = None,
) -> Path:
    """
    Build a multi-band median composite from STAC items.

    Output band order defaults to:
    B02, B03, B04, B08, B11, B12
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    bands = bands or S2_BANDS
    signed = sign_items(items)

    if not signed:
        raise ValueError("No STAC items provided for composite build.")

    stack = stackstac.stack(
        signed,
        assets=bands,
        epsg=epsg,
        resolution=resolution,
        bounds_latlon=None,
    )

    # median over time -> dims: band, y, x
    composite = stack.median(dim="time", skipna=True).astype("float32")

    composite.rio.write_crs(f"EPSG:{epsg}", inplace=True)
    composite.rio.to_raster(out_path)

    return out_path


def describe_raster(path: str | Path) -> dict:
    path = Path(path)
    with rasterio.open(path) as src:
        return {
            "path": str(path),
            "width": src.width,
            "height": src.height,
            "count": src.count,
            "crs": str(src.crs),
            "dtype": str(src.dtypes[0]),
            "bounds": tuple(src.bounds),
        }