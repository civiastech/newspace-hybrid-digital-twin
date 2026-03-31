from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(slots=True)
class WeightConfig:
    optical_weight: float = 0.4
    sar_weight: float = 0.3
    anomaly_weight: float = 0.3


def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    total = float(sum(weights.values()))
    if total <= 0:
        return {k: 0.0 for k in weights}
    return {k: float(v) / total for k, v in weights.items()}
