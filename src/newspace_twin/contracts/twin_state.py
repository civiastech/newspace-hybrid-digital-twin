from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class TwinStateContract:
    state_id: str
    unit_id: str
    timestamp: str
    fused_condition_score: float
    severity_class: str
    anomaly_score: float
    uncertainty_score: float
    risk_score: float
    priority_rank: int | None
    recommended_action: str
    previous_state_id: str | None
    state_metadata: dict[str, object] = field(default_factory=dict)
