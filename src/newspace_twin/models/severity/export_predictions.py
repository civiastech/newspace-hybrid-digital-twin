from __future__ import annotations

from pathlib import Path

import pandas as pd
import torch

from newspace_twin.datasets.loaders import ClassificationTileDataset, build_dataloader
from .model import SeverityClassifier


def export_validation_predictions(
    manifest_csv: str | Path,
    checkpoint_path: str | Path,
    output_csv: str | Path,
    device: str = "cpu",
) -> str:
    ds = ClassificationTileDataset(manifest_csv, split="val")
    loader = build_dataloader(ds, batch_size=8, shuffle=False)

    if len(ds) == 0:
        raise ValueError("Validation dataset is empty.")

    x0, _ = next(iter(loader))
    in_channels = x0.shape[1]

    model = SeverityClassifier(in_channels=in_channels, num_classes=4).to(device)

    checkpoint = torch.load(checkpoint_path, map_location=device)
    state_dict = checkpoint["model_state_dict"] if "model_state_dict" in checkpoint else checkpoint
    model.load_state_dict(state_dict)
    model.eval()

    rows = []
    offset = 0

    with torch.no_grad():
        for x, y in loader:
            x = x.to(device)
            logits = model(x)
            probs = torch.softmax(logits, dim=1)
            preds = logits.argmax(dim=1).cpu().numpy()
            probs_np = probs.cpu().numpy()
            y_np = y.cpu().numpy()

            batch_size = len(preds)
            batch_df = ds.df.iloc[offset:offset + batch_size].copy()
            offset += batch_size

            for i in range(batch_size):
                rows.append(
                    {
                        "sample_id": batch_df.iloc[i]["sample_id"],
                        "unit_id": batch_df.iloc[i]["unit_id"],
                        "split": batch_df.iloc[i]["split"],
                        "feature_group": batch_df.iloc[i].get("feature_group", ""),
                        "tile_uri": batch_df.iloc[i]["tile_uri"],
                        "true_class": int(y_np[i]),
                        "pred_class": int(preds[i]),
                        "prob_0": float(probs_np[i][0]),
                        "prob_1": float(probs_np[i][1]),
                        "prob_2": float(probs_np[i][2]),
                        "prob_3": float(probs_np[i][3]),
                        "confidence": float(probs_np[i].max()),
                        "correct": int(preds[i] == y_np[i]),
                    }
                )

    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out_path, index=False)
    return str(out_path)