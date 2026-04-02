from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio


def dnbr_to_class(dnbr: np.ndarray) -> np.ndarray:
    """
    Bootstrap wildfire severity classes from dNBR.

    Thresholds used here are practical starting values and can be refined later.
    """
    labels = np.zeros_like(dnbr, dtype=np.uint8)

    labels[(dnbr >= 0.10) & (dnbr < 0.27)] = 1
    labels[(dnbr >= 0.27) & (dnbr < 0.44)] = 2
    labels[dnbr >= 0.44] = 3

    return labels


def build_severity_labels_from_dnbr(
    dnbr_path: str | Path,
    output_path: str | Path,
) -> Path:
    dnbr_path = Path(dnbr_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(dnbr_path) as src:
        dnbr = src.read(1).astype(np.float32)
        meta = src.meta.copy()

    labels = dnbr_to_class(dnbr)

    meta.update(count=1, dtype="uint8")

    with rasterio.open(output_path, "w", **meta) as dst:
        dst.write(labels, 1)

    return output_path