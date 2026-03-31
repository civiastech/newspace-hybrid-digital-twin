from __future__ import annotations

import json

import typer

from newspace_twin.experiments.error_analysis import export_error_analysis

app = typer.Typer(help='Export per-sample error analysis for segmentation or severity models.')


@app.command()
def main(
    task: str = typer.Option(..., help='segmentation | severity'),
    manifest: str = typer.Option(..., help='Manifest CSV path.'),
    checkpoint: str = typer.Option(..., help='Model checkpoint path.'),
    split: str = typer.Option('val', help='Split to analyze.'),
    out_dir: str = typer.Option('data/reports/experiments/error_analysis'),
) -> None:
    out = export_error_analysis(manifest, checkpoint, task, out_dir, split=split)
    typer.echo(json.dumps({'artifact': out}, indent=2))


if __name__ == '__main__':
    app()
