from __future__ import annotations

import shutil
from pathlib import Path

from newspace_twin.api.services import generate_decision_outputs, run_fusion, run_twin_update
from newspace_twin.validation_runtime.reports import build_validation_report


def main() -> None:
    out_root = Path("artifacts/smoke")
    if out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    fusion = run_fusion(
        {
            "scores": {"optical": 0.82, "sar": 0.61, "anomaly": 0.74},
            "confidences": {"optical": 0.92, "sar": 0.78, "anomaly": 0.70},
            "timestamps_iso": {
                "optical": "2026-03-30T09:00:00",
                "sar": "2026-03-30T09:15:00",
                "anomaly": "2026-03-30T09:20:00",
            },
        }
    )

    previous_state = run_twin_update(
        {
            "unit_id": "cell_001",
            "timestamp_iso": "2026-03-28T10:00:00",
            "fused_condition_score": 0.48,
            "severity_class": "medium",
            "anomaly_score": 0.31,
            "uncertainty_score": 0.16,
            "consistency_score": 0.84,
            "state_metadata": {"scenario": "smoke_previous"},
        }
    )

    current_state = run_twin_update(
        {
            "unit_id": "cell_001",
            "timestamp_iso": "2026-03-30T10:00:00",
            "fused_condition_score": fusion["fused_condition_score"],
            "severity_class": "high",
            "anomaly_score": 0.74,
            "uncertainty_score": fusion["uncertainty_score"],
            "consistency_score": fusion["consistency_score"],
            "previous_state": previous_state,
            "state_metadata": {"scenario": "smoke_current"},
        }
    )

    second_state = {
        "unit_id": "cell_002",
        "timestamp": "2026-03-30T10:00:00",
        "risk_score": 0.42,
        "priority_rank": 2,
        "fused_condition_score": 0.45,
        "severity_class": "medium",
        "recommended_action": "scheduled_monitoring",
        "uncertainty_score": 0.12,
        "consistency_score": 0.88,
        "geometry": {"type": "Point", "coordinates": [1.0, 1.0]},
    }

    current_state["geometry"] = {"type": "Point", "coordinates": [0.0, 0.0]}
    states = [current_state, second_state]
    decision_outputs = generate_decision_outputs(states, str(out_root / "decision_outputs"))
    validation_outputs = build_validation_report(
        [
            {
                "unit_id": previous_state["unit_id"],
                "timestamp": previous_state["timestamp"],
                "risk_score": previous_state["risk_score"],
                "uncertainty_score": previous_state["uncertainty_score"],
                "consistency_score": previous_state["consistency_score"],
            },
            {
                "unit_id": current_state["unit_id"],
                "timestamp": current_state["timestamp"],
                "risk_score": current_state["risk_score"],
                "uncertainty_score": current_state["uncertainty_score"],
                "consistency_score": current_state["consistency_score"],
            },
            {
                "unit_id": second_state["unit_id"],
                "timestamp": second_state["timestamp"],
                "risk_score": second_state["risk_score"],
                "uncertainty_score": second_state["uncertainty_score"],
                "consistency_score": second_state["consistency_score"],
            },
        ],
        out_root / "validation_runtime",
    )

    print("Smoke run completed")
    print({"fusion": fusion, "decision_outputs": decision_outputs, "validation_outputs": validation_outputs})


if __name__ == "__main__":
    main()
