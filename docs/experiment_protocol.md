# Deliverable 2B Experiment Protocol

## Objective
Run tracked baseline experiments for segmentation, severity classification, and anomaly scoring, then compare runs with reproducible reports.

## Required artifacts
- experiment registry JSONL
- per-run JSON and Markdown reports
- model comparison summary
- task-level error analysis CSV

## CLI sequence
```bash
python scripts/run_experiment.py --config configs/experiments/segmentation_baseline.yaml
python scripts/run_experiment.py --config configs/experiments/severity_baseline.yaml
python scripts/compare_models.py
python scripts/error_analysis.py --task segmentation --manifest data/manifests/wildfire_case_aoi/dataset_manifest.csv --checkpoint data/reports/checkpoints/segmentation.pt
```

## Tracking backends
The default backend is `local_jsonl`. Optional MLflow and W&B tracking can be enabled from `configs/experiments/tracking.yaml` if those packages are installed.
