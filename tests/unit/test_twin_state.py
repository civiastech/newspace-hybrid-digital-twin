from datetime import datetime, timedelta

from newspace_twin.twin.updater import update_twin_state
from newspace_twin.twin.risk import compute_risk_score, classify_priority
from newspace_twin.twin.actions import recommend_action


def test_risk_score_bounds():
    score = compute_risk_score(0.8, 0.6, 0.2, 0.7)
    assert 0.0 <= score <= 1.0


def test_priority_classification():
    level, rank = classify_priority(0.9)
    assert level == "critical"
    assert rank == 1


def test_action_logic():
    action = recommend_action("high", "high", 0.2)
    assert action == "priority_intervention"


def test_state_update_with_history():
    t0 = datetime.utcnow() - timedelta(days=1)
    prev = update_twin_state(
        unit_id="cell_001",
        timestamp=t0,
        fused_condition_score=0.30,
        severity_class="low",
        anomaly_score=0.20,
        uncertainty_score=0.10,
        consistency_score=0.90,
    )
    curr = update_twin_state(
        unit_id="cell_001",
        timestamp=datetime.utcnow(),
        fused_condition_score=0.70,
        severity_class="high",
        anomaly_score=0.60,
        uncertainty_score=0.20,
        consistency_score=0.75,
        previous_state=prev,
    )
    assert curr.previous_state_id is not None
    assert "delta_risk_score" in curr.state_metadata
    assert curr.priority_rank in {1, 2, 3, 4}
