from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PredictionContract:
    prediction_id: str
    unit_id: str
    timestamp: str
    model_family: str
    model_version: str
    output_type: str
    prediction_values: dict[str, float | int | str]
    confidence: float | None
    source_sample_id: str
