from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn
from torch.utils.data import DataLoader


@dataclass(slots=True)
class TrainConfig:
    epochs: int = 2
    batch_size: int = 4
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    device: str = 'cpu'


def train_one_epoch(model: nn.Module, loader: DataLoader, criterion: nn.Module, optimizer: torch.optim.Optimizer, device: str = 'cpu') -> float:
    model.to(device)
    model.train()
    total_loss = 0.0
    n_batches = 0
    for x, y in loader:
        x = x.to(device)
        y = y.to(device)
        optimizer.zero_grad(set_to_none=True)
        preds = model(x)
        loss = criterion(preds, y)
        loss.backward()
        optimizer.step()
        total_loss += float(loss.item())
        n_batches += 1
    return total_loss / max(1, n_batches)
