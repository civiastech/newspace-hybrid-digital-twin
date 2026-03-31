from __future__ import annotations

from pathlib import Path
from typing import Iterable


def build_decision_summary_markdown(states: Iterable[dict], output_path: str | Path) -> Path:
    rows = sorted(
        list(states),
        key=lambda row: (row.get('priority_rank', 999), -float(row.get('risk_score', 0.0))),
    )
    lines = ['# Decision Support Summary', '', f'Total units assessed: {len(rows)}', '']

    if rows:
        top = rows[0]
        lines.extend([
            '## Highest Priority Unit',
            f"- Unit ID: {top.get('unit_id', 'unknown')}",
            f"- Risk score: {top.get('risk_score', 0.0)}",
            f"- Severity class: {top.get('severity_class', 'unknown')}",
            f"- Recommended action: {top.get('recommended_action', 'unknown')}",
            '',
        ])

    lines.append('## Ranked Units')
    lines.append('')
    for row in rows:
        lines.append(
            f"- {row.get('unit_id', 'unknown')}: risk={row.get('risk_score', 0.0)}, "
            f"priority={row.get('priority_rank', 'NA')}, action={row.get('recommended_action', 'unknown')}"
        )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines), encoding='utf-8')
    return output_path
