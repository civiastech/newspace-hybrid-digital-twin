from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class ObservationContract:
    observation_id: str
    aoi_id: str
    modality: str
    acquisition_time: str | None
    source_uri: str
    checksum: str
    crs_epsg: int | None
    footprint_wkt: str | None
    metadata: dict[str, object] = field(default_factory=dict)
    lineage_parent_id: str | None = None
    status: str = "raw"
    ingested_at: datetime = field(default_factory=lambda: datetime.now(UTC))
