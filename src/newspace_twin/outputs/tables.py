from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path


def rank_states(states: Iterable[dict]) -> list[dict]:
    ranked = sorted(
        [dict(state) for state in states],
        key=lambda row: (
            row.get('priority_rank', 999),
            -float(row.get('risk_score', 0.0)),
            -float(row.get('fused_condition_score', 0.0)),
        ),
    )
    for index, row in enumerate(ranked, start=1):
        row['global_rank'] = index
    return ranked


def export_ranked_table_csv(states: Iterable[dict], output_path: str | Path) -> Path:
    rows = rank_states(states)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output_path.write_text('', encoding='utf-8')
        return output_path
    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with output_path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    return output_path
