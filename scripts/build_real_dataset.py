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
    majority_idx = np.argmax(counts)
    return int(values[majority_idx]), int(counts[majority_idx]), tile.size


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

    # how much class 0 to keep relative to all minority tiles
    class0_multiplier = 4.0

    print("Loading features...")
    feature_stack, _ = stack_features(aoi_id)

    print("Loading labels...")
    label_path = Path("data/labels") / aoi_id / "severity_labels.tif"
    with rasterio.open(label_path) as src:
        labels = src.read(1)

    print("Tiling...")
    tiles = tile_array(feature_stack, tile_size)

    all_records = []

    for idx, (i, j, tile) in enumerate(tiles):
        tile = np.nan_to_num(tile, nan=0.0, posinf=0.0, neginf=0.0)
        tile = np.clip(tile, -1.0, 1.0)

        if np.all(tile == 0):
            continue

        label, majority_count, n_pixels = get_tile_label(labels, i, j, tile_size)
        majority_fraction = majority_count / n_pixels

        sample_id = f"sample_{len(all_records):06d}"
        unit_id = f"unit_{len(all_records):06d}"

        all_records.append(
            {
                "sample_id": sample_id,
                "unit_id": unit_id,
                "row": i,
                "col": j,
                "tile": tile,
                "class_id": label,
                "true_class": label,
                "majority_fraction": majority_fraction,
            }
        )

        if idx % 500 == 0:
            print(f"Scanned {idx} tiles...")

    df = pd.DataFrame(all_records)

    if df.empty:
        raise ValueError("No usable tiles were created.")

    print("\nRaw class distribution:")
    print(df["class_id"].value_counts().sort_index())

    # Keep all minority classes
    minority_df = df[df["class_id"] != 0].copy()
    class0_df = df[df["class_id"] == 0].copy()

    # Optional: keep purer minority tiles
    #minority_df = minority_df[minority_df["majority_fraction"] >= 0.50].copy()

    n_minority = len(minority_df)
    max_class0 = int(class0_multiplier * n_minority)

    if len(class0_df) > max_class0 and max_class0 > 0:
        class0_df = class0_df.sample(n=max_class0, random_state=42)

    balanced_df = pd.concat([class0_df, minority_df], ignore_index=True)
    balanced_df = balanced_df.sample(frac=1.0, random_state=42).reset_index(drop=True)

    # reassign sample/unit ids after balancing
    balanced_df["sample_id"] = [f"sample_{i:06d}" for i in range(len(balanced_df))]
    balanced_df["unit_id"] = [f"unit_{i:06d}" for i in range(len(balanced_df))]
    balanced_df["split"] = [assign_split(i, len(balanced_df)) for i in range(len(balanced_df))]
    balanced_df["feature_group"] = "optical_real_stack"

    out_dir = Path("data/processed") / aoi_id / "tiles"
    out_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for idx, row in balanced_df.iterrows():
        sample_id = row["sample_id"]
        tile_path = out_dir / f"{sample_id}.npy"
        np.save(tile_path, row["tile"].astype(np.float32))

        records.append(
            {
                "sample_id": row["sample_id"],
                "unit_id": row["unit_id"],
                "split": row["split"],
                "feature_group": row["feature_group"],
                "tile_uri": str(tile_path),
                "class_id": int(row["class_id"]),
                "true_class": int(row["true_class"]),
            }
        )

    manifest_df = pd.DataFrame(records)

    manifest_dir = Path("data/manifests") / aoi_id
    manifest_dir.mkdir(parents=True, exist_ok=True)

    csv_path = manifest_dir / "dataset_manifest.csv"
    manifest_df.to_csv(csv_path, index=False)

    print("\nBalanced dataset built successfully!")
    print(f"Total tiles: {len(manifest_df)}")
    print(f"Saved to: {csv_path}")

    print("\nBalanced class distribution:")
    print(manifest_df["class_id"].value_counts().sort_index())

    print("\nSplit distribution:")
    print(manifest_df["split"].value_counts())

    print("\nClass distribution by split:")
    print(pd.crosstab(manifest_df["split"], manifest_df["class_id"]))


if __name__ == "__main__":
    main()