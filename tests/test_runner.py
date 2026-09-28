from pathlib import Path

from flaky_investigator.models import Verdict
from flaky_investigator.runner import investigate


def test_classifies_consistent_passes(tmp_path: Path) -> None:
    result = investigate(
        ("python", "-c", "raise SystemExit(0)"),
        runs=4,
        cwd=tmp_path,
    )

    assert result.verdict is Verdict.STABLE_PASS
    assert result.pass_count == 4
    assert result.fail_count == 0


def test_classifies_consistent_failures(tmp_path: Path) -> None:
    result = investigate(
        ("python", "-c", "raise SystemExit(3)"),
        runs=3,
        cwd=tmp_path,
    )

    assert result.verdict is Verdict.STABLE_FAIL
    assert result.pass_count == 0
    assert result.fail_count == 3
    assert {run.exit_code for run in result.runs} == {3}


def test_classifies_mixed_results_as_flaky(tmp_path: Path) -> None:
    script = tmp_path / "alternating.py"
    script.write_text(
        "from pathlib import Path\n"
        "counter = Path('counter.txt')\n"
        "value = int(counter.read_text()) if counter.exists() else 0\n"
        "value += 1\n"
        "counter.write_text(str(value))\n"
        "raise SystemExit(value % 2)\n",
        encoding="utf-8",
    )

    result = investigate(
        ("python", str(script)),
        runs=4,
        cwd=tmp_path,
    )

    assert result.verdict is Verdict.FLAKY
    assert result.pass_count == 2
    assert result.fail_count == 2


def test_timeout_is_preserved_as_its_own_verdict(tmp_path: Path) -> None:
    result = investigate(
        ("python", "-c", "import time; time.sleep(0.2)"),
        runs=2,
        cwd=tmp_path,
        timeout_seconds=0.01,
    )

    assert result.verdict is Verdict.TIMEOUT
    assert result.timeout_count == 2
