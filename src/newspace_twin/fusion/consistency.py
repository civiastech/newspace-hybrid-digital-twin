from __future__ import annotations

import numpy as np


def consistency_score(scores: dict[str, float | None]) -> float:
    values = [float(v) for v in scores.values() if v is not None]
    if len(values) <= 1:
        return 1.0
    std = float(np.std(values))
    return float(1.0 / (1.0 + std))
