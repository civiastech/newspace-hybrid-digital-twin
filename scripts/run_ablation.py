from __future__ import annotations

from pathlib import Path

import typer
import yaml

from newspace_twin.experiments.ablation import export_ablation_reports

app = typer.Typer(help="Build ablation reports from experiment registry.")


@app.command()
def main(registry: str = 'data/reports/experiments/experiment_registry.jsonl', config: str = 'configs/experiments/ablation.yaml', out_dir: str = 'data/reports/experiments/ablation') -> None:
    raw = yaml.safe_load(Path(config).read_text(encoding='utf-8'))
    result = export_ablation_reports(registry_path=Path(registry), out_dir=Path(out_dir), factor=str(raw['factor']), metric_map=dict(raw['metric_map']), maximize=dict(raw.get('maximize', {})))
    typer.echo(result)


if __name__ == '__main__':
    app()
