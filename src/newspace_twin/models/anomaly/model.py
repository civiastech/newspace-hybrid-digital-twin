from __future__ import annotations

import torch
from torch import nn


class Autoencoder(nn.Module):
    def __init__(self, input_dim: int = 8, hidden_dim: int = 16) -> None:
        super().__init__()
        self.encoder = nn.Sequential(nn.Linear(input_dim, hidden_dim), nn.ReLU(inplace=True), nn.Linear(hidden_dim, hidden_dim // 2), nn.ReLU(inplace=True))
        self.decoder = nn.Sequential(nn.Linear(hidden_dim // 2, hidden_dim), nn.ReLU(inplace=True), nn.Linear(hidden_dim, input_dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.encoder(x)
        return self.decoder(z)


def build_model(input_dim: int = 8, hidden_dim: int = 16) -> nn.Module:
    return Autoencoder(input_dim=input_dim, hidden_dim=hidden_dim)
