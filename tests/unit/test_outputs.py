import json
from pathlib import Path

from newspace_twin.outputs.geojson import states_to_geojson
from newspace_twin.outputs.reports import build_decision_summary_markdown
from newspace_twin.outputs.tables import export_ranked_table_csv, rank_states


def sample_states():
    return [
        {
            "unit_id": "cell_001",
            "risk_score": 0.88,
            "priority_rank": 1,
            "fused_condition_score": 0.82,
            "severity_class": "high",
            "recommended_action": "immediate_field_review",
            "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
        },
        {
            "unit_id": "cell_002",
            "risk_score": 0.55,
            "priority_rank": 3,
            "fused_condition_score": 0.51,
            "severity_class": "medium",
            "recommended_action": "scheduled_monitoring",
            "geometry": {"type": "Point", "coordinates": [1.0, 1.0]},
        },
    ]

def test_rank_states():
    ranked = rank_states(sample_states())
    assert ranked[0]["unit_id"] == "cell_001"
    assert ranked[0]["global_rank"] == 1

def test_geojson_export(tmp_path: Path):
    out = states_to_geojson(sample_states(), tmp_path / "states.geojson")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 2

def test_report_and_csv(tmp_path: Path):
    csv_path = export_ranked_table_csv(sample_states(), tmp_path / "ranked.csv")
    md_path = build_decision_summary_markdown(sample_states(), tmp_path / "summary.md")
    assert csv_path.exists()
    assert md_path.exists()
