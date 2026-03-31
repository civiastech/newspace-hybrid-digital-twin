from __future__ import annotations

import torch


def anomaly_score(model: torch.nn.Module, x: torch.Tensor) -> torch.Tensor:
    model.eval()
    with torch.no_grad():
        recon = model(x)
        return ((recon - x) ** 2).mean(dim=1)
