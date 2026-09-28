import argparse
from pathlib import Path

from .runner import investigate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flaky-test-investigator",
        description=(
            "Repeat a verification command and classify observed stability."
        ),
    )
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--cwd", type=Path, default=Path("."))
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Verification command, normally supplied after --.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    command = tuple(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        print("error: provide a verification command after --")
        return 2

    try:
        result = investigate(
            command,
            runs=args.runs,
            cwd=args.cwd,
            timeout_seconds=args.timeout,
        )
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    print(f"verdict: {result.verdict.value}")
    print(
        f"runs={len(result.runs)} "
        f"pass={result.pass_count} "
        f"fail={result.fail_count} "
        f"timeout={result.timeout_count}"
    )
    print(f"average_duration={result.average_duration_seconds:.3f}s")

    for run in result.runs:
        state = "pass" if run.passed else "fail"
        if run.timed_out:
            state = "timeout"
        print(
            f"- run={run.run_number} {state} "
            f"exit={run.exit_code} "
            f"duration={run.duration_seconds:.3f}s"
        )

    return 0 if result.verdict.value == "stable-pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
