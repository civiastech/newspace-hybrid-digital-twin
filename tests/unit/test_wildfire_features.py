import numpy as np
import pandas as pd

from newspace_twin.features.wildfire_features import (
    build_optical_feature_stack,
    build_sar_feature_stack,
    summarize_sensor_csv,
)


def test_sensor_summary():
    df = pd.DataFrame(
        {
            "temperature_c": [20, 25, 30],
            "humidity_pct": [60, 50, 40],
            "smoke_ppm": [5, 15, 25],
            "wind_mps": [2, 3, 4],
        }
    )
    result = summarize_sensor_csv(df)
    assert "temp_mean" in result
    assert result["smoke_max"] == 25.0


def test_optical_stack(tmp_path):
    h, w = 8, 8
    pre_path = tmp_path / "pre.npz"
    post_path = tmp_path / "post.npz"

    np.savez_compressed(
        pre_path,
        red=np.ones((h, w), dtype=np.float32) * 0.2,
        green=np.ones((h, w), dtype=np.float32) * 0.3,
        nir=np.ones((h, w), dtype=np.float32) * 0.7,
        swir=np.ones((h, w), dtype=np.float32) * 0.4,
    )
    np.savez_compressed(
        post_path,
        red=np.ones((h, w), dtype=np.float32) * 0.3,
        green=np.ones((h, w), dtype=np.float32) * 0.25,
        nir=np.ones((h, w), dtype=np.float32) * 0.5,
        swir=np.ones((h, w), dtype=np.float32) * 0.6,
    )

    stack = build_optical_feature_stack(str(pre_path), str(post_path))
    assert stack.shape == (9, h, w)


def test_sar_stack(tmp_path):
    h, w = 8, 8
    pre_path = tmp_path / "pre_s1.npz"
    post_path = tmp_path / "post_s1.npz"

    np.savez_compressed(
        pre_path,
        vv=np.ones((h, w), dtype=np.float32) * 0.5,
        vh=np.ones((h, w), dtype=np.float32) * 0.2,
    )
    np.savez_compressed(
        post_path,
        vv=np.ones((h, w), dtype=np.float32) * 0.4,
        vh=np.ones((h, w), dtype=np.float32) * 0.1,
    )

    stack = build_sar_feature_stack(str(pre_path), str(post_path))
    assert stack.shape == (9, h, w)
