from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(slots=True)
class TemporalFeatureResult:
    source_uri: str
    output_uri: str
    rows: int


def build_temporal_features(source_path: str | Path, output_path: str | Path) -> TemporalFeatureResult:
    """Create simple temporal deltas per sensor from preprocessed time-series."""
    src_path = Path(source_path)
    dst_path = Path(output_path)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(src_path)
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, errors='coerce')
    numeric_cols = [c for c in df.columns if c not in {'sensor_id', 'timestamp'} and pd.api.types.is_numeric_dtype(df[c])]
    if 'sensor_id' in df.columns:
        df = df.sort_values(['sensor_id', 'timestamp']).copy()
        for col in numeric_cols:
            df[f'{col}_delta'] = df.groupby('sensor_id')[col].diff().fillna(0.0)
            df[f'{col}_rolling_mean_2'] = df.groupby('sensor_id')[col].transform(lambda s: s.rolling(2, min_periods=1).mean())
    df.to_csv(dst_path, index=False)
    return TemporalFeatureResult(source_uri=str(src_path), output_uri=str(dst_path), rows=int(len(df)))
