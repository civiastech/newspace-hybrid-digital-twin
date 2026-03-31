from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(slots=True)
class DatasetStats:
    sample_count: int
    unique_units: int
    split_counts: dict[str, int]
    average_bands: float


def compute_dataset_stats(df: pd.DataFrame) -> DatasetStats:
    split_counts = {str(k): int(v) for k, v in df['split'].value_counts(dropna=False).to_dict().items()} if 'split' in df.columns else {}
    avg_bands = float(df['bands'].mean()) if 'bands' in df.columns and not df.empty else 0.0
    return DatasetStats(
        sample_count=int(len(df)),
        unique_units=int(df['unit_id'].nunique()) if 'unit_id' in df.columns else 0,
        split_counts=split_counts,
        average_bands=avg_bands,
    )
