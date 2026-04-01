from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset


@dataclass(slots=True)
class AugmentationConfig:
    hflip: bool = False
    vflip: bool = False
    noise_std: float = 0.0


class NumpyAugment:
    def __init__(self, cfg: AugmentationConfig) -> None:
        self.cfg = cfg

    def __call__(self, x: np.ndarray, y: np.ndarray | int | float | None = None):
        out_x = x.copy()
        out_y = None if y is None else (y.copy() if isinstance(y, np.ndarray) else y)
        if self.cfg.hflip and np.random.rand() < 0.5:
            out_x = np.flip(out_x, axis=2).copy()
            if isinstance(out_y, np.ndarray):
                out_y = np.flip(out_y, axis=1).copy()
        if self.cfg.vflip and np.random.rand() < 0.5:
            out_x = np.flip(out_x, axis=1).copy()
            if isinstance(out_y, np.ndarray):
                out_y = np.flip(out_y, axis=0).copy()
        if self.cfg.noise_std > 0:
            out_x = out_x + np.random.normal(0.0, self.cfg.noise_std, size=out_x.shape).astype(out_x.dtype)
        return out_x, out_y


class SegmentationTileDataset(Dataset[tuple[torch.Tensor, torch.Tensor]]):
    def __init__(self, manifest_csv: str | Path, split: str = 'train', transform: Callable | None = None) -> None:
        self.df = pd.read_csv(manifest_csv)
        self.df = self.df[(self.df['split'] == split) & self.df['label_uri'].notna()].reset_index(drop=True)
        self.transform = transform

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        row = self.df.iloc[idx]
        x = np.load(row['tile_uri']).astype(np.float32)
        y = np.load(row['label_uri']).astype(np.float32)
        if y.ndim == 3:
            y = y[0]
        if self.transform is not None:
            x, y = self.transform(x, y)
        return torch.from_numpy(x), torch.from_numpy(y[None, ...])


class ClassificationTileDataset(Dataset[tuple[torch.Tensor, torch.Tensor]]):
    def __init__(self, manifest_csv: str | Path, split: str = 'train', transform: Callable | None = None) -> None:
        self.df = pd.read_csv(manifest_csv)
        self.df = self.df[self.df['split'] == split].reset_index(drop=True)
        self.transform = transform

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        row = self.df.iloc[idx]
        x = np.load(row['tile_uri']).astype(np.float32)
        label = int(row.get('class_id', 0))
        if self.transform is not None:
            x, _ = self.transform(x, None)
        return torch.from_numpy(x), torch.tensor(label, dtype=torch.long)


class AnomalySeriesDataset(Dataset[tuple[torch.Tensor, torch.Tensor]]):
    def __init__(self, features_csv: str | Path) -> None:
        self.df = pd.read_csv(features_csv)
        feature_cols = [c for c in self.df.columns if c not in {'sample_id', 'split', 'target'}]
        self.x = self.df[feature_cols].astype('float32').to_numpy()
        self.y = self.df.get('target', pd.Series(np.zeros(len(self.df), dtype=np.float32))).astype('float32').to_numpy()

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        return torch.from_numpy(self.x[idx]), torch.tensor(self.y[idx], dtype=torch.float32)


def build_dataloader(dataset: Dataset, batch_size: int = 4, shuffle: bool = False) -> DataLoader:
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        collate_fn=classification_collate_fn,
    )


def _pad_tensor_to_shape(x: torch.Tensor, target_h: int, target_w: int) -> torch.Tensor:
    c, h, w = x.shape
    out = torch.zeros((c, target_h, target_w), dtype=x.dtype)

    h_use = min(h, target_h)
    w_use = min(w, target_w)

    out[:, :h_use, :w_use] = x[:, :h_use, :w_use]
    return out


def classification_collate_fn(batch):
    xs, ys = zip(*batch)

    max_h = max(x.shape[1] for x in xs)
    max_w = max(x.shape[2] for x in xs)

    xs_padded = [_pad_tensor_to_shape(x, max_h, max_w) for x in xs]

    x_batch = torch.stack(xs_padded, dim=0)
    y_batch = torch.stack(list(ys), dim=0)

    return x_batch, y_batch