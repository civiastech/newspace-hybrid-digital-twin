from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class DatasetSampleContract:
    sample_id: str
    unit_id: str
    split: str
    task_type: str
    input_uris: list[str]
    label_uri: str | None
    feature_uri: str | None
    source_observation_ids: list[str]
    metadata: dict[str, object] = field(default_factory=dict)
