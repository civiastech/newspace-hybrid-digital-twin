from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "newspace_twin_api"

class FusionRequest(BaseModel):
    scores: dict[str, float]
    confidences: dict[str, float]
    timestamps_iso: dict[str, str]

class FusionResponse(BaseModel):
    fused_condition_score: float
    uncertainty_score: float
    consistency_score: float
    weights: dict[str, float]

class TwinUpdateRequest(BaseModel):
    unit_id: str
    timestamp_iso: str
    fused_condition_score: float
    severity_class: str
    anomaly_score: float
    uncertainty_score: float
    consistency_score: float
    previous_state: dict[str, Any] | None = None
    state_metadata: dict[str, Any] = Field(default_factory=dict)

class DecisionOutputRequest(BaseModel):
    states: list[dict[str, Any]]

class DecisionOutputResponse(BaseModel):
    ranked_count: int
    top_unit_id: str | None = None
    output_dir: str
