from __future__ import annotations

import json

import typer

from newspace_twin.experiments.runner import run_experiment

app = typer.Typer(help='Run a tracked experiment and write structured reports.')


@app.command()
def main(config: str = typer.Option(..., help='Path to experiment YAML config.')) -> None:
    result = run_experiment(config)
    typer.echo(json.dumps(result, indent=2))


if __name__ == '__main__':
    app()
