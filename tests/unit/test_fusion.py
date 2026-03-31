
from datetime import datetime, timedelta
from newspace_twin.fusion import fuse_scores
from newspace_twin.fusion.weighting import WeightConfig

def test_fusion_basic():
    now = datetime.utcnow()

    scores = {"optical": 0.8, "sar": 0.6, "anomaly": 0.7}
    confidences = {"optical": 0.9, "sar": 0.8, "anomaly": 0.7}
    timestamps = {
        "optical": now,
        "sar": now - timedelta(days=2),
        "anomaly": now - timedelta(days=1),
    }

    result = fuse_scores(scores, confidences, timestamps, now, WeightConfig())

    assert "fused_condition_score" in result
    assert 0 <= result["uncertainty_score"] <= 1
