from pathlib import Path

from newspace_twin.outputs.figures import build_risk_summary_figure
from newspace_twin.outputs.geojson import states_to_geojson
from newspace_twin.outputs.reports import build_decision_summary_markdown
from newspace_twin.outputs.tables import export_ranked_table_csv


def sample_states():
    return [
        {
            "unit_id": "cell_001",
            "risk_score": 0.88,
            "priority_rank": 1,
            "fused_condition_score": 0.82,
            "severity_class": "high",
            "recommended_action": "immediate_field_review",
            "geometry": {"type": "Polygon", "coordinates": [[[0,0],[1,0],[1,1],[0,1],[0,0]]]},
        },
        {
            "unit_id": "cell_002",
            "risk_score": 0.62,
            "priority_rank": 2,
            "fused_condition_score": 0.60,
            "severity_class": "medium",
            "recommended_action": "scheduled_monitoring",
            "geometry": {"type": "Polygon", "coordinates": [[[1,0],[2,0],[2,1],[1,1],[1,0]]]},
        },
    ]

def main() -> None:
    states = sample_states()
    out_dir = Path("data/reports/decision_outputs")
    export_ranked_table_csv(states, out_dir / "ranked_assets.csv")
    states_to_geojson(states, out_dir / "ranked_assets.geojson")
    build_risk_summary_figure(states, out_dir / "risk_summary.png")
    build_decision_summary_markdown(states, out_dir / "decision_summary.md")
    print(f"Decision outputs written to {out_dir}")

if __name__ == "__main__":
    main()
