from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from .comparison import build_comparison_table, summarize_best_runs
from .reports import write_markdown_report


def build_benchmark_summary(registry_path: str | Path, metric_map: dict[str, str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    summary = summarize_best_runs(registry_path, metric_map)
    for task, payload in summary.get('tasks', {}).items():
        rows.append({
            'task': task,
            'selection_metric': payload['selection_metric'],
            'best_value': payload['best_value'],
            'run_id': payload['run_id'],
            'run_name': payload['run_name'],
        })
    return pd.DataFrame(rows)


def export_benchmark_assets(registry_path: str | Path, out_dir: str | Path, metric_map: dict[str, str]) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    summary_df = build_benchmark_summary(registry_path, metric_map)
    csv_path = out / 'benchmark_summary.csv'
    md_path = out / 'benchmark_summary.md'
    summary_df.to_csv(csv_path, index=False)
    write_markdown_report(md_path, 'Benchmark Summary', {'rows': summary_df.to_dict(orient='records')})
    figure_paths: dict[str, str] = {}
    for task, metric_name in metric_map.items():
        table = build_comparison_table(registry_path, metric_name)
        task_table = table[table['task'] == task].dropna(subset=['metric_value'])
        if task_table.empty:
            continue
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(task_table['run_name'].astype(str).tolist(), task_table['metric_value'].astype(float).tolist())
        ax.set_title(f'{task.title()} benchmark')
        ax.set_ylabel(metric_name)
        ax.set_xlabel('Run')
        ax.tick_params(axis='x', rotation=30)
        fig.tight_layout()
        fig_path = out / f'{task}_benchmark.png'
        fig.savefig(fig_path, dpi=200)
        plt.close(fig)
        figure_paths[f'{task}_figure'] = str(fig_path)
    return {'summary_csv': str(csv_path), 'summary_md': str(md_path), **figure_paths}
