from datetime import datetime, timedelta
from pathlib import Path

from newspace_twin.twin.persistence import save_states_jsonl
from newspace_twin.twin.updater import update_twin_state


def main() -> None:
    now = datetime.utcnow()
    previous = update_twin_state(
        unit_id="cell_001",
        timestamp=now - timedelta(days=2),
        fused_condition_score=0.42,
        severity_class="medium",
        anomaly_score=0.30,
        uncertainty_score=0.15,
        consistency_score=0.85,
    )

    current = update_twin_state(
        unit_id="cell_001",
        timestamp=now,
        fused_condition_score=0.76,
        severity_class="high",
        anomaly_score=0.63,
        uncertainty_score=0.22,
        consistency_score=0.71,
        previous_state=previous,
    )

    out = Path("data/twin/example_states.jsonl")
    save_states_jsonl([previous, current], out)
    print(f"Saved twin states to {out}")


if __name__ == "__main__":
    main()
