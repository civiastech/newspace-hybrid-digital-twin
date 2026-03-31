from __future__ import annotations

import torch


def dice_score(probs: torch.Tensor, target: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    probs_bin = (probs >= 0.5).float()
    intersection = (probs_bin * target).sum()
    union = probs_bin.sum() + target.sum()
    return (2 * intersection + eps) / (union + eps)


def iou_score(probs: torch.Tensor, target: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    probs_bin = (probs >= 0.5).float()
    intersection = (probs_bin * target).sum()
    union = probs_bin.sum() + target.sum() - intersection
    return (intersection + eps) / (union + eps)


def classification_metrics(preds: torch.Tensor, target: torch.Tensor, num_classes: int) -> dict:
    preds = preds.cpu()
    target = target.cpu()
    accuracy = float((preds == target).float().mean().item())
    f1s = []
    for cls in range(num_classes):
        tp = ((preds == cls) & (target == cls)).sum().item()
        fp = ((preds == cls) & (target != cls)).sum().item()
        fn = ((preds != cls) & (target == cls)).sum().item()
        precision = tp / max(1, tp + fp)
        recall = tp / max(1, tp + fn)
        if precision + recall == 0:
            f1s.append(0.0)
        else:
            f1s.append(2 * precision * recall / (precision + recall))
    return {'accuracy': accuracy, 'macro_f1': float(sum(f1s) / len(f1s))}
