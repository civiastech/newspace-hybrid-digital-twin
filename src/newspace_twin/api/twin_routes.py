from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/twin", tags=["twin"])


@router.get("/health")
def twin_health():
    return {"status": "ok", "service": "digital_twin"}


@router.get("/latest-risk-layer")
def latest_risk_layer():
    path = Path("data/twin/wildfire_case_aoi/risk_layer.geojson")
    return {"exists": path.exists(), "path": str(path)}


@router.get("/latest-evolution-layer")
def latest_evolution_layer():
    path = Path("data/twin/wildfire_case_aoi/risk_evolution.geojson")
    return {"exists": path.exists(), "path": str(path)}


@router.get("/latest-alert-layer")
def latest_alert_layer():
    path = Path("data/twin/wildfire_case_aoi/alert_layer.geojson")
    return {"exists": path.exists(), "path": str(path)}