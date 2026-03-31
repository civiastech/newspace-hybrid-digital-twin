from __future__ import annotations

from pathlib import Path

import torch
from torch import nn

from newspace_twin.datasets.loaders import SegmentationTileDataset, build_dataloader
from newspace_twin.training.engine import TrainConfig, train_one_epoch
from newspace_twin.training.metrics import dice_score, iou_score
from newspace_twin.training.utils import save_checkpoint
from .model import build_model


def train_segmentation(manifest_csv: str | Path, out_dir: str | Path, cfg: TrainConfig) -> dict:
    model = build_model()
    ds = SegmentationTileDataset(manifest_csv, split='train')
    loader = build_dataloader(ds, batch_size=cfg.batch_size, shuffle=True)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay)
    history = []
    for epoch in range(cfg.epochs):
        loss = train_one_epoch(model, loader, criterion, optimizer, cfg.device)
        history.append({'epoch': epoch + 1, 'loss': loss})
    x, y = next(iter(loader))
    with torch.no_grad():
        logits = model(x)
        probs = torch.sigmoid(logits)
    metrics = {
        'dice': float(dice_score(probs, y)),
        'iou': float(iou_score(probs, y)),
    }
    ckpt = Path(out_dir) / 'segmentation.pt'
    ckpt.parent.mkdir(parents=True, exist_ok=True)
    save_checkpoint(ckpt, model, optimizer, cfg, extra={'metrics': metrics, 'history': history})
    return {'checkpoint': str(ckpt), 'metrics': metrics, 'history': history}
