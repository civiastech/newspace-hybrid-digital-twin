from __future__ import annotations

import torch


def predict_mask(model: torch.nn.Module, x: torch.Tensor, threshold: float = 0.5) -> torch.Tensor:
    model.eval()
    with torch.no_grad():
        logits = model(x)
        probs = torch.sigmoid(logits)
        return (probs >= threshold).float()
