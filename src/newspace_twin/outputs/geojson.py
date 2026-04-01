from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path


def states_to_geojson(states: Iterable[dict], output_path: str | Path) -> Path:
    features = []
    for state in states:
        geometry = state.get('geometry')
        if geometry is None:
            continue
        properties = {k: v for k, v in state.items() if k != 'geometry'}
        features.append({'type': 'Feature', 'geometry': geometry, 'properties': properties})
    fc = {'type': 'FeatureCollection', 'features': features}
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(fc, indent=2), encoding='utf-8')
    return output_path
