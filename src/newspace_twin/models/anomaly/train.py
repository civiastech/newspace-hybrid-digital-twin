from __future__ import annotations

from pathlib import Path

import torch
from torch import nn

from newspace_twin.datasets.loaders import AnomalySeriesDataset, build_dataloader
from newspace_twin.training.engine import TrainConfig
from newspace_twin.training.utils import save_checkpoint

from .model import build_model


def train_anomaly_model(features_csv: str | Path, out_dir: str | Path, cfg: TrainConfig) -> dict:
    ds = AnomalySeriesDataset(features_csv)
    loader = build_dataloader(ds, batch_size=cfg.batch_size, shuffle=True)
    sample_x, _ = ds[0]
    model = build_model(input_dim=int(sample_x.numel()))
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay)
    history = []
    model.train()
    for epoch in range(cfg.epochs):
        running = 0.0
        batches = 0
        for x, _ in loader:
            x = x.to(cfg.device)
            optimizer.zero_grad(set_to_none=True)
            recon = model(x)
            loss = criterion(recon, x)
            loss.backward()
            optimizer.step()
            running += float(loss.item())
            batches += 1
        history.append({'epoch': epoch + 1, 'loss': running / max(1, batches)})
    x_batch, _ = next(iter(loader))
    with torch.no_grad():
        recon = model(x_batch)
        score = ((recon - x_batch) ** 2).mean(dim=1)
    metrics = {'mean_reconstruction_error': float(score.mean().item())}
    ckpt = Path(out_dir) / 'anomaly.pt'
    ckpt.parent.mkdir(parents=True, exist_ok=True)
    save_checkpoint(ckpt, model, optimizer, cfg, extra={'metrics': metrics, 'history': history})
    return {'checkpoint': str(ckpt), 'metrics': metrics, 'history': history}
