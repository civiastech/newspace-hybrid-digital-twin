from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import rasterio


def read_raster(path):
    with rasterio.open(path) as src:
        return src.read(1), src.meta


def stack_features(aoi_id):
    base = Path("data/features") / aoi_id / "optical"

    ndvi_pre, meta = read_raster(base / "ndvi_pre.tif")
    ndvi_post, _ = read_raster(base / "ndvi_post.tif")
    nbr_pre, _ = read_raster(base / "nbr_pre.tif")
    nbr_post, _ = read_raster(base / "nbr_post.tif")
    dnbr, _ = read_raster(base / "dnbr.tif")

    stack = np.stack(
        [
            ndvi_pre,
            ndvi_post,
            nbr_pre,
            nbr_post,
            dnbr,
        ],
        axis=0,
    )

    return stack, meta


def tile_array(arr, tile_size):
    _, h, w = arr.shape
    tiles = []

    for i in range(0, h, tile_size):
        for j in range(0, w, tile_size):
            tile = arr[:, i : i + tile_size, j : j + tile_size]

            if tile.shape[1] != tile_size or tile.shape[2] != tile_size:
                continue

            tiles.append((i, j, tile))

    return tiles


def get_tile_label(label_raster, i, j, tile_size):
    tile = label_raster[i : i + tile_size, j : j + tile_size]
    values, counts = np.unique(tile, return_counts=True)
    return int(values[np.argmax(counts)])


def assign_split(idx: int, n_total: int) -> str:
    ratio = idx / max(n_total, 1)
    if ratio < 0.70:
        return "train"
    if ratio < 0.85:
        return "val"
    return "test"


def main():
    aoi_id = "wildfire_case_aoi"
    tile_size = 128

    print("Loading features...")
    feature_stack, _ = stack_features(aoi_id)

    print("Loading labels...")
    label_path = Path("data/labels") / aoi_id / "severity_labels.tif"
    with rasterio.open(label_path) as src:
        labels = src.read(1)

    print("Tiling...")
    tiles = tile_array(feature_stack, tile_size)

    out_dir = Path("data/processed") / aoi_id / "tiles"
    out_dir.mkdir(parents=True, exist_ok=True)

    records = []
    n_total = len(tiles)

    for idx, (i, j, tile) in enumerate(tiles):
        label = get_tile_label(labels, i, j, tile_size)

        sample_id = f"sample_{idx:06d}"
        unit_id = f"unit_{idx:06d}"
        tile_path = out_dir / f"{sample_id}.npy"
        tile = np.nan_to_num(tile, nan=0.0, posinf=0.0, neginf=0.0)
        tile = np.clip(tile, -1.0, 1.0)
        np.save(tile_path, tile.astype(np.float32))

        records.append(
            {
                "sample_id": sample_id,
                "unit_id": unit_id,
                "split": assign_split(idx, n_total),
                "feature_group": "optical_real_stack",
                "tile_uri": str(tile_path),
                "class_id": label,
                "true_class": label,
            }
        )

        if idx % 500 == 0:
            print(f"Processed {idx} tiles...")

    df = pd.DataFrame(records)

    manifest_dir = Path("data/manifests") / aoi_id
    manifest_dir.mkdir(parents=True, exist_ok=True)

    csv_path = manifest_dir / "dataset_manifest.csv"
    df.to_csv(csv_path, index=False)

    print("\nDataset built successfully!")
    print(f"Total tiles: {len(df)}")
    print(f"Saved to: {csv_path}")

    print("\nOverall class distribution:")
    print(df["class_id"].value_counts().sort_index())

    print("\nSplit distribution:")
    print(df["split"].value_counts())

    print("\nClass distribution by split:")
    print(pd.crosstab(df["split"], df["class_id"]))


if __name__ == "__main__":
    main()