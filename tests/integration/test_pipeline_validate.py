from newspace_twin.pipeline import run_pipeline


def test_validate_stage_runs() -> None:
    result = run_pipeline("configs/base.yaml", "validate")
    assert result["status"] == "ok"
    assert result["stage"] == "validate"
