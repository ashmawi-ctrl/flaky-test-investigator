from dataclasses import dataclass
from enum import StrEnum


class Verdict(StrEnum):
    STABLE_PASS = "stable-pass"
    STABLE_FAIL = "stable-fail"
    FLAKY = "flaky"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class RunResult:
    run_number: int
    command: tuple[str, ...]
    exit_code: int | None
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False

    @property
    def passed(self) -> bool:
        return not self.timed_out and self.exit_code == 0


@dataclass(frozen=True)
class InvestigationResult:
    verdict: Verdict
    runs: tuple[RunResult, ...]

    @property
    def pass_count(self) -> int:
        return sum(run.passed for run in self.runs)

    @property
    def timeout_count(self) -> int:
        return sum(run.timed_out for run in self.runs)

    @property
    def fail_count(self) -> int:
        return len(self.runs) - self.pass_count - self.timeout_count

    @property
    def average_duration_seconds(self) -> float:
        return sum(run.duration_seconds for run in self.runs) / len(self.runs)
