from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from .state import TwinState


def save_states_jsonl(states: Iterable[TwinState], output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8') as handle:
        for state in states:
            handle.write(json.dumps(state.to_dict()) + '\n')
    return output_path


def load_states_jsonl(path: str | Path) -> list[dict]:
    path = Path(path)
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open('r', encoding='utf-8') as handle:
        for line in handle:
            rows.append(json.loads(line))
    return rows
