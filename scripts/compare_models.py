from __future__ import annotations

import json

import typer

from newspace_twin.experiments.comparison import export_comparison_reports

app = typer.Typer(help='Compare tracked runs and export summary reports.')


@app.command()
def main(
    registry_path: str = typer.Option('data/reports/experiments/experiment_registry.jsonl'),
    out_dir: str = typer.Option('data/reports/experiments/comparison'),
) -> None:
    result = export_comparison_reports(registry_path, out_dir)
    typer.echo(json.dumps(result, indent=2))


if __name__ == '__main__':
    app()
