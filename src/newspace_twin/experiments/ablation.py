from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .registry import load_registry
from .reports import write_json_report, write_markdown_report


def build_ablation_table(registry_path: str | Path, factor: str, metric_map: dict[str, str], maximize: dict[str, bool] | None = None) -> pd.DataFrame:
    maximize = maximize or {}
    df = load_registry(registry_path)
    if df.empty:
        return pd.DataFrame(columns=['task', 'factor', 'variant', 'run_id', 'run_name', 'metric_name', 'metric_value'])
    rows: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        task = row.get('task')
        metric_name = metric_map.get(task)
        if metric_name is None:
            continue
        metrics = row.get('metrics', {}) or {}
        tags = row.get('tags', {}) or {}
        rows.append({
            'task': task,
            'factor': factor,
            'variant': tags.get(factor, tags.get('variant', 'unspecified')),
            'run_id': row.get('run_id'),
            'run_name': row.get('run_name'),
            'metric_name': metric_name,
            'metric_value': metrics.get(metric_name),
            'maximize': bool(maximize.get(task, True)),
        })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(['task', 'metric_value'], ascending=[True, False], na_position='last')


def summarize_ablation(table: pd.DataFrame) -> dict[str, Any]:
    summary: dict[str, Any] = {'tasks': {}}
    if table.empty:
        return summary
    for task, group in table.groupby('task'):
        maximize = bool(group['maximize'].iloc[0])
        ranked = group.dropna(subset=['metric_value']).sort_values('metric_value', ascending=not maximize)
        if ranked.empty:
            continue
        best = ranked.iloc[0]
        summary['tasks'][task] = {
            'factor': str(best['factor']),
            'best_variant': str(best['variant']),
            'metric_name': str(best['metric_name']),
            'best_metric_value': float(best['metric_value']),
            'run_id': str(best['run_id']),
            'run_name': str(best['run_name']),
        }
    return summary


def export_ablation_reports(registry_path: str | Path, out_dir: str | Path, factor: str, metric_map: dict[str, str], maximize: dict[str, bool] | None = None) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    table = build_ablation_table(registry_path, factor=factor, metric_map=metric_map, maximize=maximize)
    summary = summarize_ablation(table)
    csv_path = out / 'ablation_table.csv'
    json_path = out / 'ablation_summary.json'
    md_path = out / 'ablation_summary.md'
    table.to_csv(csv_path, index=False)
    write_json_report(json_path, summary)
    write_markdown_report(md_path, 'Ablation Summary', summary)
    return {'csv': str(csv_path), 'json': str(json_path), 'md': str(md_path)}
