from __future__ import annotations

from typing import Dict

import numpy as np


def disagreement_uncertainty(scores: Dict[str, float | None]) -> float:
    values = [float(v) for v in scores.values() if v is not None]
    if len(values) <= 1:
        return 0.0
    return float(np.std(values))


def confidence_uncertainty(confidences: Dict[str, float | None]) -> float:
    values = [float(v) for v in confidences.values() if v is not None]
    if not values:
        return 1.0
    mean_conf = float(np.mean(values))
    return max(0.0, min(1.0, 1.0 - mean_conf))
