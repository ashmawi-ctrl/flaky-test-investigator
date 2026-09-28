import json

import pytest

from flaky_investigator.models import (
    InvestigationResult,
    RunResult,
    Verdict,
)
from flaky_investigator.report import percentile, render_json


def run(number: int, duration: float, exit_code: int = 0) -> RunResult:
    return RunResult(
        run_number=number,
        command=("pytest",),
        exit_code=exit_code,
        stdout="",
        stderr="",
        duration_seconds=duration,
    )


def test_percentile_interpolates_small_samples() -> None:
    assert percentile([1.0, 2.0, 3.0, 4.0], 0.5) == pytest.approx(2.5)
    assert percentile([1.0, 2.0, 3.0, 4.0], 0.95) == pytest.approx(3.85)


def test_json_report_contains_summary_timing_and_runs() -> None:
    result = InvestigationResult(
        verdict=Verdict.FLAKY,
        runs=(
            run(1, 0.1),
            run(2, 0.3, exit_code=1),
        ),
    )

    payload = json.loads(render_json(result))

    assert payload["verdict"] == "flaky"
    assert payload["summary"] == {
        "runs": 2,
        "pass": 1,
        "fail": 1,
        "timeout": 0,
    }
    assert payload["timing_seconds"]["p50"] == pytest.approx(0.2)
    assert payload["runs"][1]["exit_code"] == 1
    assert payload["runs"][0]["command"] == ["pytest"]
