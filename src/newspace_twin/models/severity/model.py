from __future__ import annotations

import torch
from torch import nn


class SeverityClassifier(nn.Module):
    def __init__(self, in_channels: int = 9, num_classes: int = 3) -> None:
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(in_channels, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(16),

            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(32),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(64),

            nn.AdaptiveAvgPool2d((1, 1)),
        )

        self.classifier = nn.Linear(64, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feats = self.features(x).flatten(1)
        return self.classifier(feats)


def build_model(in_channels: int = 9, num_classes: int = 3) -> SeverityClassifier:
    return SeverityClassifier(in_channels=in_channels, num_classes=num_classes)