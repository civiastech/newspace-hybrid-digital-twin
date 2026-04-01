from pathlib import Path

from newspace_twin.validation_runtime.consistency import evaluate_state_consistency
from newspace_twin.validation_runtime.longitudinal import build_longitudinal_summary
from newspace_twin.validation_runtime.reliability import compute_reliability_metrics
from newspace_twin.validation_runtime.reports import build_validation_report


def sample_states():
    return [
        {
            "unit_id": "cell_001",
            "timestamp": "2026-01-01T00:00:00",
            "risk_score": 0.20,
            "uncertainty_score": 0.10,
            "consistency_score": 0.90,
        },
        {
            "unit_id": "cell_001",
            "timestamp": "2026-01-10T00:00:00",
            "risk_score": 0.80,
            "uncertainty_score": 0.20,
            "consistency_score": 0.70,
        },
        {
            "unit_id": "cell_002",
            "timestamp": "2026-01-01T00:00:00",
            "risk_score": 0.45,
            "uncertainty_score": 0.15,
            "consistency_score": 0.85,
        },
    ]

def test_longitudinal_summary():
    rows = build_longitudinal_summary(sample_states())
    assert len(rows) == 2
    assert rows[0]["n_states"] >= 1

def test_consistency_detection():
    issues = evaluate_state_consistency(sample_states(), max_allowed_jump=0.5)
    assert len(issues) == 1
    assert issues[0]["issue"] == "risk_jump"

def test_reliability_metrics():
    metrics = compute_reliability_metrics(sample_states())
    assert metrics["n_states"] == 3
    assert 0.0 <= metrics["mean_uncertainty_score"] <= 1.0

def test_validation_report(tmp_path: Path):
    outputs = build_validation_report(sample_states(), tmp_path)
    for path in outputs.values():
        assert Path(path).exists()
