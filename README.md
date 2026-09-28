# Flaky Test Investigator

[![quality](https://github.com/ashmawi-ctrl/flaky-test-investigator/actions/workflows/quality.yml/badge.svg)](https://github.com/ashmawi-ctrl/flaky-test-investigator/actions/workflows/quality.yml)

A small command-line tool for repeatedly executing a test or verification command and measuring whether its behavior is stable.

The project focuses on a frustrating CI problem: a test that is green most of the time can still waste hours if failures are intermittent and the evidence from each run is lost.

The tool does **not** hide failures behind retries. It records every run and classifies the observed behavior.

## Current verdicts

- `stable-pass`: every run exited 0
- `stable-fail`: every run failed
- `flaky`: the same command produced both passes and failures
- `timeout`: at least one run exceeded the configured timeout

## Install

Python 3.11+:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

## Investigate one test

```bash
flaky-test-investigator \
  --runs 30 \
  --cwd . \
  -- python -m pytest tests/test_worker.py::test_retry -q
```

Example output:

```text
verdict: flaky
runs=30 pass=27 fail=3 timeout=0
average_duration=0.412s
- run=1 pass exit=0 duration=0.398s
- run=2 pass exit=0 duration=0.401s
- run=3 fail exit=1 duration=0.419s
...
```

The CLI returns 0 only for a stable passing command. A flaky, consistently failing, or timed-out investigation returns a non-zero status so it can be used in CI experiments.

## Why repeated execution?

A single failure only proves that one run failed.

Repeated execution helps answer a different question:

> Does the same input and command behave consistently when executed again?

That distinction matters before changing production code. A deterministic regression and an intermittent race can need very different investigations.

## Evidence captured per run

Each run records:

- run number
- exact argument vector
- exit code
- stdout
- stderr
- duration
- timeout state

The first version keeps all evidence in memory and prints a compact terminal summary. Machine-readable reports are intentionally left for a later change.

## Timeout semantics

A timeout is not silently counted as an ordinary assertion failure.

For example:

```bash
flaky-test-investigator \
  --runs 10 \
  --timeout 5 \
  -- python -m pytest tests/test_network.py -q
```

If any run exceeds five seconds, the result is classified as `timeout`.

That conservative behavior avoids calling a test "flaky" when the actual symptom may be a hang or deadlock.

## Development

```bash
make install
make quality
```

The test suite includes a deterministic alternating script that passes and fails on successive executions. That gives the flaky classification a reproducible regression test without relying on timing luck or random failures.

## Engineering workflow

The first implementation is tracked through:

- [Issue #1](https://github.com/ashmawi-ctrl/flaky-test-investigator/issues/1)
- branch `feat/repeated-test-analysis`
- deterministic pass/fail/flaky/timeout tests
- GitHub Actions lint and test checks
- a reviewable pull request

## Deliberate limitations

- executes one trusted local command
- sequential runs only
- no pytest plugin
- no random seed injection yet
- no environment snapshotting
- no CPU or memory telemetry
- no JSON/Markdown report yet
- no historical GitHub Actions ingestion

Those are deliberate boundaries. The current project answers one question clearly before adding test-runner-specific behavior.

## Next investigations

- record an explicit seed per run
- machine-readable JSON reports
- percentile timing summary
- stop-after-first-failure vs full-sample modes
- environment fingerprinting
- pytest integration
- compare failures by normalized traceback

## License

MIT
