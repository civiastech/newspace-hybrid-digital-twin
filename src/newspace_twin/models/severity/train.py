from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import confusion_matrix
from torch import nn

from newspace_twin.datasets.loaders import (
    ClassificationTileDataset,
    build_dataloader,
    build_balanced_dataloader,
)
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
        return (
            0.0,
            {
                "accuracy": 0.0,
                "macro_f1": 0.0,
                "confusion_matrix": [[0, 0, 0, 0] for _ in range(4)],
            },
        )

    preds_cat = torch.cat(all_preds)
    targets_cat = torch.cat(all_targets)

    metrics = classification_metrics(preds_cat, targets_cat, num_classes=4)
    cm = confusion_matrix(
        targets_cat.numpy(),
        preds_cat.numpy(),
        labels=[0, 1, 2, 3],
    )
    metrics["confusion_matrix"] = cm.tolist()

    return total_loss / n_batches, metrics


def train_severity_classifier(
    manifest_csv: str | Path,
    out_dir: str | Path,
    cfg: TrainConfig,
) -> dict:
    train_ds = ClassificationTileDataset(manifest_csv, split="train")
    val_ds = ClassificationTileDataset(manifest_csv, split="val")

    train_loader = build_balanced_dataloader(
        train_ds,
        batch_size=cfg.batch_size,
    )
    val_loader = build_dataloader(
        val_ds,
        batch_size=cfg.batch_size,
        shuffle=False,
    )

    x, _ = next(iter(train_loader))
    in_channels = x.shape[1]

    model = SeverityClassifier(
        in_channels=in_channels,
        num_classes=4,
    ).to(cfg.device)

    # Smoothed class-weighted loss
    class_counts = train_ds.df["class_id"].value_counts().sort_index()
    num_classes = 4
    counts = np.array(
        [class_counts.get(i, 1) for i in range(num_classes)],
        dtype=np.float32,
    )
    weights = 1.0 / np.sqrt(counts)
    weights = weights / weights.sum() * num_classes
    class_weights = torch.tensor(
        weights,
        dtype=torch.float32,
    ).to(cfg.device)

    criterion = nn.CrossEntropyLoss(weight=class_weights)

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=cfg.learning_rate,
        weight_decay=cfg.weight_decay,
    )

    history = []
    best_val_loss = float("inf")
    best_metrics = None

    best_f1 = -1.0
    best_epoch = -1
    patience = 3
    epochs_without_improvement = 0

    for epoch in range(cfg.epochs):
        train_loss = train_one_epoch(
            model,
            train_loader,
            criterion,
            optimizer,
            cfg.device,
        )
        val_loss, val_metrics = evaluate_one_epoch(
            model,
            val_loader,
            criterion,
            cfg.device,
        )

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

        current_f1 = val_metrics.get("macro_f1", 0.0)

        if current_f1 > best_f1:
            best_f1 = current_f1
            best_epoch = epoch + 1
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1

        print(
            f"\nEpoch {epoch + 1}"
            f"\ntrain_loss={train_loss:.4f}"
            f"\nval_loss={val_loss:.4f}"
            f"\nval_accuracy={val_metrics.get('accuracy', 0.0):.4f}"
            f"\nval_macro_f1={val_metrics.get('macro_f1', 0.0):.4f}"
            f"\nconfusion_matrix={val_metrics.get('confusion_matrix')}\n"
        )

        if epochs_without_improvement >= patience:
            print(
                f"Early stopping at epoch {epoch + 1}. "
                f"Best epoch was {best_epoch} with macro_f1={best_f1:.4f}"
            )
            break

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
            "class_weights": weights.tolist(),
            "best_macro_f1": best_f1,
            "best_epoch": best_epoch,
        },
    )

    return {
        "checkpoint": str(ckpt),
        "best_val_loss": best_val_loss,
        "best_val_metrics": best_metrics,
        "history": history,
        "class_weights": weights.tolist(),
        "best_macro_f1": best_f1,
        "best_epoch": best_epoch,
    }