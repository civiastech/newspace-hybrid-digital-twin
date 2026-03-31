from __future__ import annotations

import torch


def predict_class(model: torch.nn.Module, x: torch.Tensor) -> torch.Tensor:
    model.eval()
    with torch.no_grad():
        return model(x).argmax(dim=1)
