from __future__ import annotations

from fastapi import FastAPI

from .schemas import (
    DecisionOutputRequest,
    DecisionOutputResponse,
    FusionRequest,
    FusionResponse,
    HealthResponse,
    TwinUpdateRequest,
)
from .services import generate_decision_outputs, run_fusion, run_twin_update
from .twin_routes import router as twin_router

app = FastAPI(title="NewSpace Hybrid Digital Twin API", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.post("/fusion", response_model=FusionResponse)
def fusion_endpoint(payload: FusionRequest) -> FusionResponse:
    result = run_fusion(payload.model_dump())
    return FusionResponse(**result)


@app.post("/twin/update")
def twin_update_endpoint(payload: TwinUpdateRequest):
    return run_twin_update(payload.model_dump())


@app.post("/decision/outputs", response_model=DecisionOutputResponse)
def decision_outputs_endpoint(payload: DecisionOutputRequest) -> DecisionOutputResponse:
    result = generate_decision_outputs(payload.states, "data/api_outputs")
    return DecisionOutputResponse(**result)


app.include_router(twin_router)