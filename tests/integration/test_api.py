from datetime import datetime

from fastapi.testclient import TestClient

from newspace_twin.api.app import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_fusion_endpoint():
    now = datetime.utcnow().isoformat()
    payload = {
        "scores": {"optical": 0.8, "sar": 0.6, "anomaly": 0.7},
        "confidences": {"optical": 0.9, "sar": 0.8, "anomaly": 0.7},
        "timestamps_iso": {"optical": now, "sar": now, "anomaly": now},
    }
    r = client.post("/fusion", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert "fused_condition_score" in body

def test_twin_update_endpoint():
    now = datetime.utcnow().isoformat()
    payload = {
        "unit_id": "cell_001",
        "timestamp_iso": now,
        "fused_condition_score": 0.76,
        "severity_class": "high",
        "anomaly_score": 0.63,
        "uncertainty_score": 0.22,
        "consistency_score": 0.71,
        "state_metadata": {"source": "test"},
    }
    r = client.post("/twin/update", json=payload)
    assert r.status_code == 200
    assert r.json()["unit_id"] == "cell_001"

def test_decision_outputs_endpoint():
    payload = {
        "states": [
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
    }
    r = client.post("/decision/outputs", json=payload)
    assert r.status_code == 200
    assert r.json()["ranked_count"] == 2
