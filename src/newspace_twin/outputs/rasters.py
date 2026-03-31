from __future__ import annotations

from pathlib import Path


def write_stub_raster_summary(output_path: str | Path, description: str = 'Raster export hook ready.') -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(description, encoding='utf-8')
    return output_path
