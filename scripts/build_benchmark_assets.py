from __future__ import annotations

from pathlib import Path

import typer
import yaml

from newspace_twin.experiments.benchmarks import export_benchmark_assets

app = typer.Typer(help="Build benchmark tables and figures from experiment registry.")


@app.command()
def main(registry: str = 'data/reports/experiments/experiment_registry.jsonl', config: str = 'configs/experiments/benchmark.yaml', out_dir: str = 'data/reports/experiments/benchmarks') -> None:
    raw = yaml.safe_load(Path(config).read_text(encoding='utf-8'))
    result = export_benchmark_assets(registry_path=Path(registry), out_dir=Path(out_dir), metric_map=dict(raw['selection_metric_map']))
    typer.echo(result)


if __name__ == '__main__':
    app()
