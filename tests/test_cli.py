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
