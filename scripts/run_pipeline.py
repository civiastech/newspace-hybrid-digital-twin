from __future__ import annotations

import typer

from newspace_twin.pipeline import run_pipeline

app = typer.Typer(add_completion=False)


@app.command()
def main(config: str = "configs/base.yaml", stage: str = "validate") -> None:
    result = run_pipeline(config_path=config, stage=stage)
    typer.echo(result)


if __name__ == "__main__":
    app()
