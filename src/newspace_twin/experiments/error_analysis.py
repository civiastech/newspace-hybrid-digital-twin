from __future__ import annotations

from pathlib import Path

import pandas as pd
import torch

from newspace_twin.datasets.loaders import (
    ClassificationTileDataset,
    SegmentationTileDataset,
    build_dataloader,
)
from newspace_twin.models.segmentation.model import build_model as build_segmentation_model
from newspace_twin.models.severity.model import build_model as build_severity_model


def segmentation_error_report(manifest_csv: str | Path, checkpoint_path: str | Path, split: str = 'val') -> pd.DataFrame:
    ds = SegmentationTileDataset(manifest_csv, split=split)
    if len(ds) == 0:
        return pd.DataFrame(columns=['index', 'iou', 'target_pixels', 'pred_pixels'])
    loader = build_dataloader(ds, batch_size=1, shuffle=False)
    payload = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
    model = build_segmentation_model()
    model.load_state_dict(payload['model_state_dict'])
    model.eval()
    rows = []
    with torch.no_grad():
        for idx, (x, y) in enumerate(loader):
            probs = torch.sigmoid(model(x))
            pred = (probs >= 0.5).float()
            intersection = float((pred * y).sum().item())
            union = float((pred + y - pred * y).sum().item())
            iou = intersection / union if union > 0 else 1.0
            rows.append({
                'index': idx,
                'iou': iou,
                'target_pixels': float(y.sum().item()),
                'pred_pixels': float(pred.sum().item()),
            })
    return pd.DataFrame(rows).sort_values('iou')


def severity_error_report(manifest_csv: str | Path, checkpoint_path: str | Path, split: str = 'val') -> pd.DataFrame:
    ds = ClassificationTileDataset(manifest_csv, split=split)
    if len(ds) == 0:
        return pd.DataFrame(columns=['index', 'target', 'predicted', 'correct', 'confidence'])
    loader = build_dataloader(ds, batch_size=1, shuffle=False)
    payload = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
    model = build_severity_model()
    model.load_state_dict(payload['model_state_dict'])
    model.eval()
    rows = []
    with torch.no_grad():
        for idx, (x, y) in enumerate(loader):
            logits = model(x)
            probs = torch.softmax(logits, dim=1)
            conf, pred = probs.max(dim=1)
            rows.append({
                'index': idx,
                'target': int(y.item()),
                'predicted': int(pred.item()),
                'correct': bool(pred.item() == y.item()),
                'confidence': float(conf.item()),
            })
    return pd.DataFrame(rows).sort_values(['correct', 'confidence'])


def export_error_analysis(manifest_csv: str | Path, checkpoint_path: str | Path, task: str, out_dir: str | Path, split: str = 'val') -> str:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    if task == 'segmentation':
        df = segmentation_error_report(manifest_csv, checkpoint_path, split=split)
    elif task == 'severity':
        df = severity_error_report(manifest_csv, checkpoint_path, split=split)
    else:
        raise ValueError(f'Unsupported task for error analysis: {task}')
    out_path = out / f'{task}_error_analysis.csv'
    df.to_csv(out_path, index=False)
    return str(out_path)
