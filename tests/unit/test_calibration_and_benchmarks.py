from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from newspace_twin.experiments.ablation import export_ablation_reports
from newspace_twin.experiments.benchmarks import export_benchmark_assets
from newspace_twin.experiments.calibration import expected_calibration_error, reliability_table


def _write_registry(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    records = [
        {'run_id': 'r1', 'run_name': 'seg_optical', 'task': 'segmentation', 'status': 'completed', 'metrics': {'dice': 0.81}, 'tags': {'modality': 'optical'}},
        {'run_id': 'r2', 'run_name': 'seg_fused', 'task': 'segmentation', 'status': 'completed', 'metrics': {'dice': 0.87}, 'tags': {'modality': 'fused'}},
        {'run_id': 'r3', 'run_name': 'sev_optical', 'task': 'severity', 'status': 'completed', 'metrics': {'macro_f1': 0.72}, 'tags': {'modality': 'optical'}},
        {'run_id': 'r4', 'run_name': 'sev_fused', 'task': 'severity', 'status': 'completed', 'metrics': {'macro_f1': 0.78}, 'tags': {'modality': 'fused'}},
        {'run_id': 'r5', 'run_name': 'ano_baseline', 'task': 'anomaly', 'status': 'completed', 'metrics': {'mean_reconstruction_error': 0.12}, 'tags': {'modality': 'optical'}},
    ]
    with path.open('w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record) + '\n')


def test_expected_calibration_error_basic() -> None:
    conf = pd.Series([0.9, 0.8, 0.6, 0.2]).to_numpy(dtype=float)
    correct = pd.Series([1, 1, 0, 0]).to_numpy(dtype=float)
    ece = expected_calibration_error(conf, correct, bins=2)
    assert 0.0 <= ece <= 1.0
    table = reliability_table(conf, correct, bins=2)
    assert len(table) == 2
    assert int(table['count'].fillna(0).sum()) == 4


def test_ablation_and_benchmark_exports(tmp_path: Path) -> None:
    registry = tmp_path / 'experiment_registry.jsonl'
    _write_registry(registry)
    ablation = export_ablation_reports(
        registry_path=registry,
        out_dir=tmp_path / 'ablation',
        factor='modality',
        metric_map={'segmentation': 'dice', 'severity': 'macro_f1', 'anomaly': 'mean_reconstruction_error'},
        maximize={'segmentation': True, 'severity': True, 'anomaly': False},
    )
    for p in ablation.values():
        assert Path(p).exists()

    benchmark = export_benchmark_assets(
        registry_path=registry,
        out_dir=tmp_path / 'benchmarks',
        metric_map={'segmentation': 'dice', 'severity': 'macro_f1', 'anomaly': 'mean_reconstruction_error'},
    )
    for p in benchmark.values():
        assert Path(p).exists()
