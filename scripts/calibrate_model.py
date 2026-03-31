from __future__ import annotations

from pathlib import Path

import typer

from newspace_twin.experiments.calibration import export_calibration_report

app = typer.Typer(help="Export calibration diagnostics for severity classifier.")


@app.command()
def main(manifest: str, checkpoint: str, out_dir: str = 'data/reports/experiments/calibration', split: str = 'val', bins: int = 10) -> None:
    result = export_calibration_report(manifest_csv=Path(manifest), checkpoint_path=Path(checkpoint), out_dir=Path(out_dir), split=split, bins=bins)
    typer.echo(result)


if __name__ == '__main__':
    app()
