from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def validate_sensor_csv(csv_paths: list[Path], rules: dict[str, Any]) -> dict[str, object]:
    required_columns = set(rules["sensor_validation"]["required_columns"])
    timestamp_column = rules["sensor_validation"]["timestamp_column"]
    duplicate_subset = rules["sensor_validation"]["duplicate_subset"]

    missing_columns: list[dict[str, object]] = []
    duplicate_rows: list[dict[str, object]] = []
    invalid_timestamps: list[dict[str, object]] = []

    for path in csv_paths:
        frame = pd.read_csv(path)
        missing = sorted(required_columns.difference(frame.columns))
        if missing:
            missing_columns.append({"source_uri": str(path), "missing": missing})
            continue
        parsed = pd.to_datetime(frame[timestamp_column], errors="coerce", utc=True)
        invalid_count = int(parsed.isna().sum())
        if invalid_count > 0:
            invalid_timestamps.append({"source_uri": str(path), "invalid_count": invalid_count})
        duplicated = int(frame.duplicated(subset=duplicate_subset).sum()) if set(duplicate_subset).issubset(frame.columns) else 0
        if duplicated > 0:
            duplicate_rows.append({"source_uri": str(path), "duplicate_count": duplicated})

    return {
        "missing_columns": missing_columns,
        "duplicate_rows": duplicate_rows,
        "invalid_timestamps": invalid_timestamps,
    }
