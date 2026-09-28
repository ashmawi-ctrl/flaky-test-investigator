import subprocess
import time
from pathlib import Path

from .models import InvestigationResult, RunResult, Verdict


def investigate(
    command: tuple[str, ...],
    *,
    runs: int = 10,
    cwd: str | Path = ".",
    timeout_seconds: float = 60.0,
) -> InvestigationResult:
    if not command:
        raise ValueError("verification command cannot be empty")
    if runs < 2:
        raise ValueError("runs must be at least 2")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than 0")

    workdir = Path(cwd).resolve()
    if not workdir.is_dir():
        raise ValueError(f"working directory does not exist: {workdir}")

    results = tuple(
        _run_once(
            command,
            run_number=index,
            cwd=workdir,
            timeout_seconds=timeout_seconds,
        )
        for index in range(1, runs + 1)
    )

    return InvestigationResult(
        verdict=_classify(results),
        runs=results,
    )


def _run_once(
    command: tuple[str, ...],
    *,
    run_number: int,
    cwd: Path,
    timeout_seconds: float,
) -> RunResult:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return RunResult(
            run_number=run_number,
            command=command,
            exit_code=None,
            stdout=_as_text(exc.stdout),
            stderr=_as_text(exc.stderr),
            duration_seconds=time.perf_counter() - started,
            timed_out=True,
        )

    return RunResult(
        run_number=run_number,
        command=command,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        duration_seconds=time.perf_counter() - started,
    )


def _classify(runs: tuple[RunResult, ...]) -> Verdict:
    if any(run.timed_out for run in runs):
        return Verdict.TIMEOUT

    pass_count = sum(run.passed for run in runs)
    if pass_count == len(runs):
        return Verdict.STABLE_PASS
    if pass_count == 0:
        return Verdict.STABLE_FAIL
    return Verdict.FLAKY


def _as_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value
