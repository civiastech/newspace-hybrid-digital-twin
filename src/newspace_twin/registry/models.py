from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class RegistryRecord:
    dataset_id: str
    modality: str
    source_uri: str
    checksum: str
    aoi_id: str
    crs_epsg: int | None = None
    acquired_at: datetime | None = None
    ingested_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    lineage_parent_id: str | None = None
    status: str = "raw"
    metadata: dict[str, object] = field(default_factory=dict)
    footprint_wkt: str | None = None
