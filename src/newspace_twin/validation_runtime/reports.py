from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from .consistency import evaluate_state_consistency
from .longitudinal import build_longitudinal_summary
from .reliability import compute_reliability_metrics


def build_validation_report(states: Iterable[dict], output_dir: str | Path) -> dict[str, str]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    states_list = list(states)
    longitudinal = build_longitudinal_summary(states_list)
    consistency = evaluate_state_consistency(states_list)
    reliability = compute_reliability_metrics(states_list)

    long_path = output_dir / "longitudinal_summary.json"
    cons_path = output_dir / "consistency_issues.json"
    rel_path = output_dir / "reliability_metrics.json"
    md_path = output_dir / "validation_summary.md"

    long_path.write_text(json.dumps(longitudinal, indent=2), encoding="utf-8")
    cons_path.write_text(json.dumps(consistency, indent=2), encoding="utf-8")
    rel_path.write_text(json.dumps(reliability, indent=2), encoding="utf-8")

    lines = [
        "# Validation and Reliability Summary",
        "",
        f"- Total states: {reliability['n_states']}",
        f"- Mean uncertainty: {reliability['mean_uncertainty_score']}",
        f"- Mean consistency: {reliability['mean_consistency_score']}",
        f"- High-risk fraction: {reliability['high_risk_fraction']}",
        f"- Consistency issues detected: {len(consistency)}",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "longitudinal_summary": str(long_path),
        "consistency_issues": str(cons_path),
        "reliability_metrics": str(rel_path),
        "validation_summary": str(md_path),
    }
