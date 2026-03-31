from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def build_training_fixture(base_dir: str | Path) -> tuple[Path, Path]:
    base = Path(base_dir)
    tiles = base / 'tiles'
    labels = base / 'labels'
    tiles.mkdir(parents=True, exist_ok=True)
    labels.mkdir(parents=True, exist_ok=True)
    rows = []
    rng = np.random.default_rng(42)
    for idx in range(12):
        tile = rng.random((3, 32, 32), dtype=np.float32)
        mask = (tile[0] > 0.5).astype(np.float32)
        tile_path = tiles / f'tile_{idx}.npy'
        label_path = labels / f'label_{idx}.npy'
        np.save(tile_path, tile)
        np.save(label_path, mask[None, ...])
        rows.append({
            'sample_id': f's_{idx}',
            'tile_uri': str(tile_path),
            'label_uri': str(label_path),
            'split': 'train' if idx < 8 else ('val' if idx < 10 else 'test'),
            'class_id': int(idx % 3),
        })
    manifest = base / 'manifest.csv'
    pd.DataFrame(rows).to_csv(manifest, index=False)

    features = base / 'anomaly_features.csv'
    feat_rows = []
    for idx in range(12):
        record = {'sample_id': f'a_{idx}', 'split': 'train' if idx < 8 else 'test', 'target': float(idx % 2)}
        for j in range(8):
            record[f'f{j}'] = float(rng.normal())
        feat_rows.append(record)
    pd.DataFrame(feat_rows).to_csv(features, index=False)
    return manifest, features
