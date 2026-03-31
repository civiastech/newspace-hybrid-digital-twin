from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class TwinState:
    unit_id: str
    timestamp: datetime
    fused_condition_score: float
    severity_class: str
    anomaly_score: float
    uncertainty_score: float
    consistency_score: float
    risk_score: float
    priority_rank: Optional[int] = None
    recommended_action: str = 'monitor'
    previous_state_id: Optional[str] = None
    state_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        row = asdict(self)
        row['timestamp'] = self.timestamp.isoformat()
        return row


@dataclass
class StateHistoryEntry:
    state_id: str
    unit_id: str
    timestamp: datetime
    risk_score: float
    fused_condition_score: float
    severity_class: str
    recommended_action: str
    previous_state_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        row = asdict(self)
        row['timestamp'] = self.timestamp.isoformat()
        return row


def build_state_id(unit_id: str, timestamp: datetime) -> str:
    return f'{unit_id}__{timestamp.strftime("%Y%m%dT%H%M%S")}'


def state_delta(current: TwinState, previous: Optional[TwinState]) -> Dict[str, float]:
    if previous is None:
        return {
            'delta_risk_score': 0.0,
            'delta_condition_score': 0.0,
            'delta_anomaly_score': 0.0,
        }
    return {
        'delta_risk_score': float(current.risk_score - previous.risk_score),
        'delta_condition_score': float(current.fused_condition_score - previous.fused_condition_score),
        'delta_anomaly_score': float(current.anomaly_score - previous.anomaly_score),
    }
