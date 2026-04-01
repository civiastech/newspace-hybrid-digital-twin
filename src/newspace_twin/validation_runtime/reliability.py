from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def compute_reliability_metrics(states: Iterable[dict]) -> dict[str, Any]:
    rows = list(states)
    if not rows:
        return {
            "n_states": 0,
            "mean_uncertainty_score": None,
            "mean_consistency_score": None,
            "high_risk_fraction": None,
        }

    n = len(rows)
    mean_uncertainty = sum(float(r.get("uncertainty_score", 0.0)) for r in rows) / n
    mean_consistency = sum(float(r.get("consistency_score", 0.0)) for r in rows) / n
    high_risk_fraction = sum(1 for r in rows if float(r.get("risk_score", 0.0)) >= 0.65) / n

    return {
        "n_states": n,
        "mean_uncertainty_score": mean_uncertainty,
        "mean_consistency_score": mean_consistency,
        "high_risk_fraction": high_risk_fraction,
    }
