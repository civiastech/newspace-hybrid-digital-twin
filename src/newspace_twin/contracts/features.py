from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class FeatureContract:
    feature_id: str
    unit_id: str
    aoi_id: str
    timestamp: str
    feature_group: str
    feature_values: dict[str, float | int | str]
    source_observation_ids: list[str]
    quality_flags: dict[str, object] = field(default_factory=dict)
