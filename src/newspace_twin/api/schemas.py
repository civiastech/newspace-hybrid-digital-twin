from __future__ import annotations
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "newspace_twin_api"

class FusionRequest(BaseModel):
    scores: Dict[str, float]
    confidences: Dict[str, float]
    timestamps_iso: Dict[str, str]

class FusionResponse(BaseModel):
    fused_condition_score: float
    uncertainty_score: float
    consistency_score: float
    weights: Dict[str, float]

class TwinUpdateRequest(BaseModel):
    unit_id: str
    timestamp_iso: str
    fused_condition_score: float
    severity_class: str
    anomaly_score: float
    uncertainty_score: float
    consistency_score: float
    previous_state: Optional[Dict[str, Any]] = None
    state_metadata: Dict[str, Any] = Field(default_factory=dict)

class DecisionOutputRequest(BaseModel):
    states: List[Dict[str, Any]]

class DecisionOutputResponse(BaseModel):
    ranked_count: int
    top_unit_id: Optional[str] = None
    output_dir: str
