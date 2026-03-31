from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .registry import load_registry
from .reports import write_json_report, write_markdown_report


def build_comparison_table(registry_path: str | Path, metric_name: str) -> pd.DataFrame:
    df = load_registry(registry_path)
    if df.empty:
        return df
    rows: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        metrics = row.get('metrics', {}) or {}
        rows.append({
            'run_id': row['run_id'],
            'task': row['task'],
            'run_name': row['run_name'],
            'status': row['status'],
            'metric_name': metric_name,
            'metric_value': metrics.get(metric_name),
        })
    out = pd.DataFrame(rows).sort_values(['task', 'metric_value'], ascending=[True, False], na_position='last')
    return out


def summarize_best_runs(registry_path: str | Path, metric_map: dict[str, str]) -> dict[str, Any]:
    df = load_registry(registry_path)
    summary: dict[str, Any] = {'tasks': {}}
    if df.empty:
        return summary
    for task, metric_name in metric_map.items():
        task_rows = []
        for _, row in df[df['task'] == task].iterrows():
            metrics = row.get('metrics', {}) or {}
            value = metrics.get(metric_name)
            if value is not None:
                task_rows.append((float(value), row))
        if task_rows:
            best_value, best_row = sorted(task_rows, key=lambda x: x[0], reverse=True)[0]
            summary['tasks'][task] = {
                'selection_metric': metric_name,
                'best_value': best_value,
                'run_id': best_row['run_id'],
                'run_name': best_row['run_name'],
            }
    return summary


def export_comparison_reports(registry_path: str | Path, out_dir: str | Path) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    summary = summarize_best_runs(registry_path, {
        'segmentation': 'dice',
        'severity': 'macro_f1',
        'anomaly': 'mean_reconstruction_error',
    })
    seg_table = build_comparison_table(registry_path, 'dice')
    sev_table = build_comparison_table(registry_path, 'macro_f1')
    ano_table = build_comparison_table(registry_path, 'mean_reconstruction_error')
    csv_path = out / 'comparison_table.csv'
    pd.concat([seg_table, sev_table, ano_table], ignore_index=True).to_csv(csv_path, index=False)
    json_path = out / 'comparison_summary.json'
    md_path = out / 'comparison_summary.md'
    write_json_report(json_path, summary)
    write_markdown_report(md_path, 'Model Comparison Summary', summary)
    return {'csv': str(csv_path), 'json': str(json_path), 'md': str(md_path)}
