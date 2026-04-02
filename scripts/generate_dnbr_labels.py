from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio

from newspace_twin.tiling.labels_real import build_severity_labels_from_dnbr


def main() -> None:
    aoi_id = "wildfire_case_aoi"

    dnbr_path = Path("data/features") / aoi_id / "optical" / "dnbr.tif"
    label_path = Path("data/labels") / aoi_id / "severity_labels.tif"

    if not dnbr_path.exists():
        raise FileNotFoundError(f"Missing dNBR raster: {dnbr_path}")

    out = build_severity_labels_from_dnbr(dnbr_path, label_path)

    with rasterio.open(out) as src:
        labels = src.read(1)

    unique, counts = np.unique(labels, return_counts=True)

    print(f"Severity label raster created: {out}")
    print("Class distribution:")
    for cls, cnt in zip(unique.tolist(), counts.tolist()):
        print(f"  class {cls}: {cnt}")


if __name__ == "__main__":
    main()