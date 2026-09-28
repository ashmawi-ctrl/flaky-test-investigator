import json
import math
from dataclasses import asdict
from typing import Iterable

from .models import InvestigationResult


def percentile(values: Iterable[float], quantile: float) -> float:
    samples = sorted(values)
    if not samples:
        raise ValueError("cannot calculate percentile of an empty sample")
    if not 0 <= quantile <= 1:
        raise ValueError("quantile must be between 0 and 1")

    position = (len(samples) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return float(samples[lower])

    weight = position - lower
    return float(
        samples[lower] * (1 - weight) + samples[upper] * weight
    )


def result_to_dict(result: InvestigationResult) -> dict:
    durations = [run.duration_seconds for run in result.runs]
    return {
        "verdict": result.verdict.value,
        "summary": {
            "runs": len(result.runs),
            "pass": result.pass_count,
            "fail": result.fail_count,
            "timeout": result.timeout_count,
        },
        "timing_seconds": {
            "average": result.average_duration_seconds,
            "p50": percentile(durations, 0.50),
            "p95": percentile(durations, 0.95),
            "max": max(durations),
        },
        "runs": [
            {
                **asdict(run),
                "command": list(run.command),
            }
            for run in result.runs
        ],
    }


def render_json(result: InvestigationResult) -> str:
    return json.dumps(result_to_dict(result), indent=2)
