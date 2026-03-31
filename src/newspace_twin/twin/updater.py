from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from newspace_twin.settings.config import AppConfig
from newspace_twin.settings.paths import ensure_project_paths

from .actions import recommend_action
from .risk import classify_priority, compute_risk_score
from .state import TwinState, build_state_id, state_delta


def update_twin_state(
    unit_id: str,
    timestamp: datetime,
    fused_condition_score: float,
    severity_class: str,
    anomaly_score: float,
    uncertainty_score: float,
    consistency_score: float,
    previous_state: Optional[TwinState] = None,
    state_metadata: Optional[Dict[str, Any]] = None,
) -> TwinState:
    risk_score = compute_risk_score(
        fused_condition_score=fused_condition_score,
        anomaly_score=anomaly_score,
        uncertainty_score=uncertainty_score,
        consistency_score=consistency_score,
    )
    risk_level, priority_rank = classify_priority(risk_score)
    action = recommend_action(severity_class=severity_class, risk_level=risk_level, uncertainty_score=uncertainty_score)

    state = TwinState(
        unit_id=unit_id,
        timestamp=timestamp,
        fused_condition_score=float(fused_condition_score),
        severity_class=severity_class,
        anomaly_score=float(anomaly_score),
        uncertainty_score=float(uncertainty_score),
        consistency_score=float(consistency_score),
        risk_score=float(risk_score),
        priority_rank=priority_rank,
        recommended_action=action,
        previous_state_id=build_state_id(previous_state.unit_id, previous_state.timestamp) if previous_state else None,
        state_metadata=dict(state_metadata or {}),
    )
    state.state_metadata.update(state_delta(state, previous_state))
    state.state_metadata['risk_level'] = risk_level
    state.state_metadata['state_id'] = build_state_id(unit_id, timestamp)
    return state


def run_twin_update(config: AppConfig) -> dict[str, object]:
    paths = ensure_project_paths(config)
    output = Path(paths['twin']) / config.active_aoi / 'twin_update_status.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        'status': 'ready',
        'message': 'Twin state engine available via update_twin_state().',
    }
    output.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    return {'twin_update_status': str(output)}
