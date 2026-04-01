from __future__ import annotations

from pathlib import Path

import torch
from torch import nn

from newspace_twin.datasets.loaders import ClassificationTileDataset, build_dataloader
from newspace_twin.training.engine import TrainConfig, train_one_epoch
from newspace_twin.training.metrics import classification_metrics
from newspace_twin.training.utils import save_checkpoint

from .model import SeverityClassifier


def evaluate_one_epoch(
    model: torch.nn.Module,
    loader,
    criterion,
    device: str,
) -> tuple[float, dict]:
    model.eval()

    total_loss = 0.0
    n_batches = 0

    all_preds = []
    all_targets = []

    with torch.no_grad():
        for x, y in loader:
            x = x.to(device)
            y = y.to(device)

            logits = model(x)
            loss = criterion(logits, y)

            total_loss += float(loss.item())
            n_batches += 1

            preds = logits.argmax(dim=1)
            all_preds.append(preds.cpu())
            all_targets.append(y.cpu())

    if n_batches == 0:
        return 0.0, {"accuracy": 0.0, "macro_f1": 0.0}

    preds_cat = torch.cat(all_preds)
    targets_cat = torch.cat(all_targets)

    metrics = classification_metrics(preds_cat, targets_cat, num_classes=4)
    return total_loss / n_batches, metrics


def train_severity_classifier(manifest_csv: str | Path, out_dir: str | Path, cfg: TrainConfig) -> dict:
    train_ds = ClassificationTileDataset(manifest_csv, split="train")
    val_ds = ClassificationTileDataset(manifest_csv, split="val")

    train_loader = build_dataloader(train_ds, batch_size=cfg.batch_size, shuffle=True)
    val_loader = build_dataloader(val_ds, batch_size=cfg.batch_size, shuffle=False)

    x, _ = next(iter(train_loader))
    in_channels = x.shape[1]

    model = SeverityClassifier(in_channels=in_channels, num_classes=4).to(cfg.device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=cfg.learning_rate,
        weight_decay=cfg.weight_decay,
    )

    history = []
    best_val_loss = float("inf")
    best_metrics = None

    for epoch in range(cfg.epochs):
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer, cfg.device)
        val_loss, val_metrics = evaluate_one_epoch(model, val_loader, criterion, cfg.device)

        row = {
            "epoch": epoch + 1,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "val_metrics": val_metrics,
        }
        history.append(row)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_metrics = val_metrics

        print(
            f"Epoch {epoch + 1}: "
            f"train_loss={train_loss:.4f}, "
            f"val_loss={val_loss:.4f}, "
            f"val_macro_f1={val_metrics.get('macro_f1', 0.0):.4f}"
        )

    ckpt = Path(out_dir) / "severity.pt"
    ckpt.parent.mkdir(parents=True, exist_ok=True)
    save_checkpoint(
        ckpt,
        model,
        optimizer,
        cfg,
        extra={
            "best_val_loss": best_val_loss,
            "best_val_metrics": best_metrics,
            "history": history,
        },
    )

    return {
        "checkpoint": str(ckpt),
        "best_val_loss": best_val_loss,
        "best_val_metrics": best_metrics,
        "history": history,
    }
