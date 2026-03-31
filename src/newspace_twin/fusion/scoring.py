from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import json

from newspace_twin.settings.config import AppConfig
from newspace_twin.settings.paths import ensure_project_paths

from .consistency import consistency_score
from .recency import exponential_decay
from .uncertainty import confidence_uncertainty, disagreement_uncertainty
from .weighting import WeightConfig, normalize_weights


def fuse_scores(
    scores: Dict[str, float | None],
    confidences: Dict[str, float | None],
    timestamps: Dict[str, datetime | None],
    current_time: datetime,
    config: WeightConfig,
) -> Dict[str, Any]:
    base_weights = {
        'optical': config.optical_weight,
        'sar': config.sar_weight,
        'anomaly': config.anomaly_weight,
    }

    active_weights: Dict[str, float] = {}
    cleaned_scores: Dict[str, float] = {}

    for key, base_weight in base_weights.items():
        score = scores.get(key)
        ts = timestamps.get(key)
        if score is None or ts is None:
            continue
        confidence = float(confidences.get(key, 1.0) or 0.0)
        weight = float(base_weight) * confidence * exponential_decay(current_time, ts)
        active_weights[key] = weight
        cleaned_scores[key] = float(score)

    normalized_weights = normalize_weights(active_weights)
    fused_score = float(sum(cleaned_scores[k] * normalized_weights[k] for k in normalized_weights)) if normalized_weights else 0.0

    raw_uncertainty = 0.5 * disagreement_uncertainty(scores) + 0.5 * confidence_uncertainty(confidences)
    uncertainty = max(0.0, min(1.0, raw_uncertainty))
    consistency = max(0.0, min(1.0, consistency_score(scores)))

    return {
        'fused_condition_score': fused_score,
        'uncertainty_score': uncertainty,
        'consistency_score': consistency,
        'weights': normalized_weights,
    }


def run_fusion_stage(config: AppConfig) -> dict[str, object]:
    paths = ensure_project_paths(config)
    output = Path(paths['reports']) / config.active_aoi / 'fusion_stage_status.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        'status': 'ready',
        'message': 'Fusion engine with recency, uncertainty, and consistency scoring is available.',
    }
    output.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    return {'fusion_status': str(output)}
