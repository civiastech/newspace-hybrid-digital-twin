from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from newspace_twin.fusion.scoring import fuse_scores
from newspace_twin.fusion.weighting import WeightConfig
from newspace_twin.outputs.geojson import states_to_geojson
from newspace_twin.outputs.reports import build_decision_summary_markdown
from newspace_twin.outputs.tables import export_ranked_table_csv, rank_states
from newspace_twin.twin.updater import update_twin_state


def run_fusion(payload: dict[str, Any]) -> dict[str, Any]:
    now = datetime.utcnow()
    timestamps = {
        k: datetime.fromisoformat(v.replace("Z", "+00:00")) if isinstance(v, str) and ("+" in v or v.endswith("Z"))
        else datetime.fromisoformat(v)
        for k, v in payload["timestamps_iso"].items()
    }
    result = fuse_scores(
        scores=payload["scores"],
        confidences=payload["confidences"],
        timestamps=timestamps,
        current_time=now,
        config=WeightConfig(),
    )
    return result

def run_twin_update(payload: dict[str, Any]):
    prev = payload.get("previous_state")
    previous_state_obj = None
    if prev:
        from newspace_twin.twin.state import TwinState
        previous_state_obj = TwinState(
            unit_id=prev["unit_id"],
            timestamp=datetime.fromisoformat(prev["timestamp"]),
            fused_condition_score=float(prev["fused_condition_score"]),
            severity_class=prev["severity_class"],
            anomaly_score=float(prev["anomaly_score"]),
            uncertainty_score=float(prev["uncertainty_score"]),
            consistency_score=float(prev["consistency_score"]),
            risk_score=float(prev["risk_score"]),
            priority_rank=prev.get("priority_rank"),
            recommended_action=prev.get("recommended_action", "monitor"),
            previous_state_id=prev.get("previous_state_id"),
            state_metadata=prev.get("state_metadata", {}),
        )
    state = update_twin_state(
        unit_id=payload["unit_id"],
        timestamp=datetime.fromisoformat(payload["timestamp_iso"]),
        fused_condition_score=float(payload["fused_condition_score"]),
        severity_class=payload["severity_class"],
        anomaly_score=float(payload["anomaly_score"]),
        uncertainty_score=float(payload["uncertainty_score"]),
        consistency_score=float(payload["consistency_score"]),
        previous_state=previous_state_obj,
        state_metadata=payload.get("state_metadata", {}),
    )
    return state.to_dict()

def generate_decision_outputs(states: list[dict[str, Any]], output_dir: str) -> dict[str, Any]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ranked = rank_states(states)
    export_ranked_table_csv(ranked, out_dir / "ranked_assets.csv")
    states_to_geojson(ranked, out_dir / "ranked_assets.geojson")
    build_decision_summary_markdown(ranked, out_dir / "decision_summary.md")
    top_unit_id = ranked[0]["unit_id"] if ranked else None
    return {"ranked_count": len(ranked), "top_unit_id": top_unit_id, "output_dir": str(out_dir)}
