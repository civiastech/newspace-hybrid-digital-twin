from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

from newspace_twin.datasets.loaders import ClassificationTileDataset, build_dataloader
from newspace_twin.models.severity.model import build_model as build_severity_model


def expected_calibration_error(confidence: np.ndarray, correct: np.ndarray, bins: int = 10) -> float:
    edges = np.linspace(0.0, 1.0, bins + 1)
    ece = 0.0
    n = max(1, confidence.size)
    for i in range(bins):
        left, right = edges[i], edges[i + 1]
        mask = (confidence >= left) & ((confidence < right) if i < bins - 1 else (confidence <= right))
        if not np.any(mask):
            continue
        bin_acc = float(correct[mask].mean())
        bin_conf = float(confidence[mask].mean())
        ece += (mask.sum() / n) * abs(bin_acc - bin_conf)
    return float(ece)


def reliability_table(confidence: np.ndarray, correct: np.ndarray, bins: int = 10) -> pd.DataFrame:
    edges = np.linspace(0.0, 1.0, bins + 1)
    rows: list[dict[str, Any]] = []
    for i in range(bins):
        left, right = float(edges[i]), float(edges[i + 1])
        mask = (confidence >= left) & ((confidence < right) if i < bins - 1 else (confidence <= right))
        count = int(mask.sum())
        if count == 0:
            rows.append({'bin_index': i, 'bin_left': left, 'bin_right': right, 'count': 0, 'accuracy': None, 'avg_confidence': None, 'gap': None})
            continue
        acc = float(correct[mask].mean())
        conf = float(confidence[mask].mean())
        rows.append({'bin_index': i, 'bin_left': left, 'bin_right': right, 'count': count, 'accuracy': acc, 'avg_confidence': conf, 'gap': abs(acc - conf)})
    return pd.DataFrame(rows)


def collect_severity_probabilities(manifest_csv: str | Path, checkpoint_path: str | Path, split: str = 'val') -> pd.DataFrame:
    ds = ClassificationTileDataset(manifest_csv, split=split)
    if len(ds) == 0:
        return pd.DataFrame(columns=['index', 'target', 'predicted', 'confidence', 'correct'])
    loader = build_dataloader(ds, batch_size=1, shuffle=False)
    payload = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
    model = build_severity_model()
    model.load_state_dict(payload['model_state_dict'])
    model.eval()
    rows = []
    with torch.no_grad():
        for idx, (x, y) in enumerate(loader):
            probs = torch.softmax(model(x), dim=1)
            conf, pred = probs.max(dim=1)
            rows.append({'index': idx, 'target': int(y.item()), 'predicted': int(pred.item()), 'confidence': float(conf.item()), 'correct': int(pred.item() == y.item())})
    return pd.DataFrame(rows)


def export_calibration_report(manifest_csv: str | Path, checkpoint_path: str | Path, out_dir: str | Path, split: str = 'val', bins: int = 10) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    probs_df = collect_severity_probabilities(manifest_csv, checkpoint_path, split=split)
    confidence = probs_df['confidence'].to_numpy(dtype=float) if not probs_df.empty else np.array([], dtype=float)
    correct = probs_df['correct'].to_numpy(dtype=float) if not probs_df.empty else np.array([], dtype=float)
    table = reliability_table(confidence, correct, bins=bins)
    ece = expected_calibration_error(confidence, correct, bins=bins) if confidence.size else 0.0
    summary = {
        'samples': int(confidence.size),
        'bins': int(bins),
        'expected_calibration_error': float(ece),
        'avg_confidence': float(confidence.mean()) if confidence.size else None,
        'accuracy': float(correct.mean()) if correct.size else None,
    }
    table_path = out / 'severity_reliability_bins.csv'
    summary_path = out / 'severity_calibration_summary.json'
    plot_path = out / 'severity_reliability_curve.png'
    probs_path = out / 'severity_probabilities.csv'
    table.to_csv(table_path, index=False)
    probs_df.to_csv(probs_path, index=False)
    summary_path.write_text(__import__('json').dumps(summary, indent=2), encoding='utf-8')

    fig, ax = plt.subplots(figsize=(6, 6))
    valid = table.dropna(subset=['accuracy', 'avg_confidence'])
    ax.plot([0, 1], [0, 1])
    if not valid.empty:
        ax.plot(valid['avg_confidence'].to_numpy(), valid['accuracy'].to_numpy(), marker='o')
    ax.set_xlabel('Confidence')
    ax.set_ylabel('Accuracy')
    ax.set_title('Severity Reliability Curve')
    fig.tight_layout()
    fig.savefig(plot_path, dpi=200)
    plt.close(fig)
    return {'summary_json': str(summary_path), 'bins_csv': str(table_path), 'plot_png': str(plot_path), 'probabilities_csv': str(probs_path)}
