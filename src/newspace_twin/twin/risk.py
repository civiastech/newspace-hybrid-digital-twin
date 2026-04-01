from __future__ import annotations


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def compute_risk_score(
    fused_condition_score: float,
    anomaly_score: float,
    uncertainty_score: float,
    consistency_score: float,
    condition_weight: float = 0.45,
    anomaly_weight: float = 0.30,
    uncertainty_weight: float = 0.15,
    inconsistency_weight: float = 0.10,
) -> float:
    inconsistency = 1.0 - clamp01(consistency_score)
    score = (
        condition_weight * clamp01(fused_condition_score)
        + anomaly_weight * clamp01(anomaly_score)
        + uncertainty_weight * clamp01(uncertainty_score)
        + inconsistency_weight * inconsistency
    )
    return clamp01(score)


def classify_priority(risk_score: float) -> tuple[str, int]:
    score = clamp01(risk_score)
    if score >= 0.85:
        return 'critical', 1
    if score >= 0.65:
        return 'high', 2
    if score >= 0.40:
        return 'medium', 3
    return 'low', 4
