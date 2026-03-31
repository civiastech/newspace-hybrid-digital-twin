from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def load_registry(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        return pd.DataFrame()
    records = [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]
    return pd.DataFrame(records)
