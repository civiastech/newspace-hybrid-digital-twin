from pathlib import Path
from newspace_twin.validation_runtime.reports import build_validation_report

def sample_states():
    return [
        {
            "unit_id": "cell_001",
            "timestamp": "2026-01-01T00:00:00",
            "risk_score": 0.35,
            "uncertainty_score": 0.18,
            "consistency_score": 0.84,
        },
        {
            "unit_id": "cell_001",
            "timestamp": "2026-01-15T00:00:00",
            "risk_score": 0.72,
            "uncertainty_score": 0.24,
            "consistency_score": 0.74,
        },
        {
            "unit_id": "cell_002",
            "timestamp": "2026-01-01T00:00:00",
            "risk_score": 0.40,
            "uncertainty_score": 0.12,
            "consistency_score": 0.88,
        },
        {
            "unit_id": "cell_002",
            "timestamp": "2026-01-15T00:00:00",
            "risk_score": 0.46,
            "uncertainty_score": 0.14,
            "consistency_score": 0.86,
        },
    ]

def main() -> None:
    out_dir = Path("data/reports/validation_runtime")
    paths = build_validation_report(sample_states(), out_dir)
    for k, v in paths.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
