from __future__ import annotations
from typing import Iterable, Dict, Any, List

def evaluate_state_consistency(states: Iterable[dict], max_allowed_jump: float = 0.5) -> List[dict]:
    rows = sorted(list(states), key=lambda x: (x["unit_id"], x["timestamp"]))
    issues = []
    previous_by_unit = {}

    for row in rows:
        uid = row["unit_id"]
        risk = float(row.get("risk_score", 0.0))
        prev = previous_by_unit.get(uid)
        if prev is not None:
            jump = abs(risk - float(prev.get("risk_score", 0.0)))
            if jump > max_allowed_jump:
                issues.append({
                    "unit_id": uid,
                    "timestamp": row["timestamp"],
                    "issue": "risk_jump",
                    "jump": jump,
                    "previous_risk_score": float(prev.get("risk_score", 0.0)),
                    "current_risk_score": risk,
                })
        previous_by_unit[uid] = row
    return issues
