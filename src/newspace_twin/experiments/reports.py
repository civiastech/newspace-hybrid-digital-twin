from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json_report(path: str | Path, payload: dict[str, Any]) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    return str(p)


def write_markdown_report(path: str | Path, title: str, sections: dict[str, Any]) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    lines = [f'# {title}', '']
    for key, value in sections.items():
        lines.append(f'## {key}')
        lines.append('')
        if isinstance(value, dict):
            lines.append('```json')
            lines.append(json.dumps(value, indent=2))
            lines.append('```')
        else:
            lines.append(str(value))
        lines.append('')
    p.write_text('\n'.join(lines), encoding='utf-8')
    return str(p)
