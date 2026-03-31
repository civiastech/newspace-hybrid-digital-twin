from __future__ import annotations

from pathlib import Path
from typing import Mapping

import matplotlib.pyplot as plt


def build_benchmark_bar_chart(metrics: Mapping[str, float], output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    labels = list(metrics.keys())
    values = [float(metrics[k]) for k in labels]
    plt.figure(figsize=(8, 4.5))
    plt.bar(labels, values)
    plt.ylabel('Score')
    plt.title('Benchmark Metrics')
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path
