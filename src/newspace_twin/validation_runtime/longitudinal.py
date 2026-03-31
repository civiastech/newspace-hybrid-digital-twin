from __future__ import annotations
from collections import defaultdict
from typing import Iterable, Dict, Any, List

def build_longitudinal_summary(states: Iterable[dict]) -> List[dict]:
    grouped = defaultdict(list)
    for s in states:
        grouped[s["unit_id"]].append(s)

    summaries = []
    for unit_id, rows in grouped.items():
        rows = sorted(rows, key=lambda x: x["timestamp"])
        first = rows[0]
        last = rows[-1]
        summaries.append({
            "unit_id": unit_id,
            "n_states": len(rows),
            "first_timestamp": first["timestamp"],
            "last_timestamp": last["timestamp"],
            "first_risk_score": float(first.get("risk_score", 0.0)),
            "last_risk_score": float(last.get("risk_score", 0.0)),
            "risk_delta": float(last.get("risk_score", 0.0)) - float(first.get("risk_score", 0.0)),
            "max_risk_score": max(float(r.get("risk_score", 0.0)) for r in rows),
            "mean_risk_score": sum(float(r.get("risk_score", 0.0)) for r in rows) / len(rows),
        })
    return summaries
