from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(slots=True)
class TimeSeriesPreprocessResult:
    source_uri: str
    output_uri: str
    rows_in: int
    rows_out: int
    duplicate_rows_removed: int
    missing_timestamps_removed: int


def preprocess_timeseries(
    source_path: str | Path,
    output_path: str | Path,
    *,
    rules: dict[str, Any],
) -> TimeSeriesPreprocessResult:
    src_path = Path(source_path)
    dst_path = Path(output_path)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    ts_cfg = rules.get('sensor_preprocessing', {})
    val_cfg = rules.get('sensor_validation', {})
    ts_col = val_cfg.get('timestamp_column', 'timestamp')
    duplicate_subset = val_cfg.get('duplicate_subset', ['sensor_id', ts_col])
    sensor_id_col = ts_cfg.get('sensor_id_column', 'sensor_id')
    resample_rule = ts_cfg.get('resample_rule', '1h')
    aggregate_method = ts_cfg.get('aggregate_method', 'mean')

    df = pd.read_csv(src_path)
    rows_in = int(len(df))
    df[ts_col] = pd.to_datetime(df[ts_col], errors='coerce', utc=True)
    missing_ts_removed = int(df[ts_col].isna().sum())
    df = df.dropna(subset=[ts_col]).copy()
    before_dedup = len(df)
    df = df.drop_duplicates(subset=duplicate_subset).copy()
    duplicate_rows_removed = int(before_dedup - len(df))
    df = df.sort_values([sensor_id_col, ts_col]).copy()

    value_columns = [col for col in df.columns if col not in {sensor_id_col, ts_col}]
    numeric_columns = [col for col in value_columns if pd.api.types.is_numeric_dtype(df[col])]

    if sensor_id_col in df.columns and numeric_columns:
        frames: list[pd.DataFrame] = []
        for sensor_id, sensor_df in df.groupby(sensor_id_col):
            sensor_df = sensor_df.set_index(ts_col)
            agg_input = sensor_df[numeric_columns]
            if aggregate_method == 'median':
                aggregated = agg_input.resample(resample_rule).median()
            elif aggregate_method == 'max':
                aggregated = agg_input.resample(resample_rule).max()
            else:
                aggregated = agg_input.resample(resample_rule).mean()
            aggregated = aggregated.reset_index()
            aggregated[sensor_id_col] = sensor_id
            frames.append(aggregated)
        df = pd.concat(frames, ignore_index=True) if frames else df
        ordered_cols = [sensor_id_col, ts_col, *numeric_columns]
        df = df[ordered_cols]

    df.to_csv(dst_path, index=False)
    return TimeSeriesPreprocessResult(
        source_uri=str(src_path),
        output_uri=str(dst_path),
        rows_in=rows_in,
        rows_out=int(len(df)),
        duplicate_rows_removed=duplicate_rows_removed,
        missing_timestamps_removed=missing_ts_removed,
    )
