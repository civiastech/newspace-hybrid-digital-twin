from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset


class UnifiedWildfireDataset(Dataset):
    def __init__(self, data_root: str, split: str = "train"):
        self.data_root = Path(data_root)
        self.split = split

        self.samples = list(self._load_samples())

    def _load_samples(self):
        # This reads from processed/interim later
        for file in (self.data_root / "processed").rglob("*.npz"):
            yield file

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        file = self.samples[idx]
        data = np.load(file)

        # Example fusion
        features = []

        if "sentinel2" in data:
            features.append(data["sentinel2"])

        if "sentinel1" in data:
            features.append(data["sentinel1"])

        if "uav" in data:
            features.append(data["uav"])

        x = np.concatenate(features, axis=0)

        y = data.get("label", np.array([0]))

        return {
            "x": torch.tensor(x, dtype=torch.float32),
            "y": torch.tensor(y, dtype=torch.long),
            "id": file.stem,
        }
