import json
from pathlib import Path

from flaky_investigator.cli import main


def test_cli_returns_zero_for_stable_pass(tmp_path: Path, capsys) -> None:
    exit_code = main(
        [
            "--runs",
            "2",
            "--cwd",
            str(tmp_path),
            "--",
            "python",
            "-c",
            "raise SystemExit(0)",
        ]
    )

    assert exit_code == 0
    assert "verdict: stable-pass" in capsys.readouterr().out


def test_cli_rejects_single_run(tmp_path: Path, capsys) -> None:
    exit_code = main(
        [
            "--runs",
            "1",
            "--cwd",
            str(tmp_path),
            "--",
            "python",
            "-c",
            "raise SystemExit(0)",
        ]
    )

    assert exit_code == 2
    assert "runs must be at least 2" in capsys.readouterr().out


def test_cli_json_output_matches_written_report(
    tmp_path: Path,
    capsys,
) -> None:
    output = tmp_path / "reports" / "investigation.json"

    exit_code = main(
        [
            "--runs",
            "2",
            "--cwd",
            str(tmp_path),
            "--format",
            "json",
            "--output",
            str(output),
            "--",
            "python",
            "-c",
            "raise SystemExit(0)",
        ]
    )

    assert exit_code == 0
    stdout = capsys.readouterr().out
    payload = json.loads(stdout)
    written = json.loads(output.read_text(encoding="utf-8"))
    assert payload == written
    assert payload["summary"]["pass"] == 2
