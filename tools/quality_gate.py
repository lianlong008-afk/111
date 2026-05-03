#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run project checks and write a Markdown quality report."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import subprocess
import sys
from typing import Iterable, List


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "reports" / "quality_report.md"


@dataclass
class CheckResult:
    name: str
    command: List[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def passed(self) -> bool:
        return self.returncode == 0

    @property
    def status(self) -> str:
        return "PASS" if self.passed else "FAIL"


def run_command(name: str, command: List[str]) -> CheckResult:
    process = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    return CheckResult(
        name=name,
        command=command,
        returncode=process.returncode,
        stdout=process.stdout.strip(),
        stderr=process.stderr.strip(),
    )


def git_output(args: Iterable[str]) -> str:
    process = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if process.returncode != 0:
        return process.stderr.strip() or "unavailable"
    return process.stdout.strip() or "clean"


def build_checks() -> List[tuple[str, List[str]]]:
    offline_smoke = (
        "from pickup_master_v24 import PickupMasterV24; "
        "m = PickupMasterV24(api_key=''); "
        "session = m.start_session('quality_gate'); "
        "status = m.get_status(); "
        "analysis = m.analyze_interest('哈哈 今天很开心~ 你呢？'); "
        "assert session == status['current_session']; "
        "assert analysis['score'] >= 50; "
        "print('v24 offline smoke ok')"
    )
    return [
        ("Python compileall", [sys.executable, "-m", "compileall", "-q", "."]),
        ("Viking filesystem regression", [sys.executable, "tests/viking_filesystem_regression.py"]),
        ("V24 offline smoke", [sys.executable, "-c", offline_smoke]),
    ]


def format_block(text: str) -> str:
    return text if text else "(empty)"


def write_report(report_path: Path, results: List[CheckResult], ideas: List[str]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    passed = all(result.passed for result in results)
    branch = git_output(["branch", "--show-current"])
    status = git_output(["status", "--short"])
    diff_stat = git_output(["diff", "--stat"])

    lines: List[str] = [
        "# Quality Gate Report",
        "",
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}",
        f"- Branch: `{branch}`",
        f"- Overall: `{'PASS' if passed else 'FAIL'}`",
        "",
        "## Iteration Ideas",
        "",
    ]

    for idea in ideas:
        lines.append(f"- {idea}")

    lines.extend([
        "",
        "## Check Summary",
        "",
        "| Check | Status | Exit Code |",
        "|---|---:|---:|",
    ])

    for result in results:
        lines.append(f"| {result.name} | `{result.status}` | `{result.returncode}` |")

    lines.extend([
        "",
        "## Git Snapshot",
        "",
        "### Changed Files",
        "",
        "```text",
        format_block(status),
        "```",
        "",
        "### Diff Stat",
        "",
        "```text",
        format_block(diff_stat),
        "```",
        "",
        "## Check Details",
        "",
    ])

    for result in results:
        lines.extend([
            f"### {result.name}",
            "",
            f"- Status: `{result.status}`",
            f"- Command: `{' '.join(result.command)}`",
            "",
            "stdout:",
            "",
            "```text",
            format_block(result.stdout),
            "```",
            "",
            "stderr:",
            "",
            "```text",
            format_block(result.stderr),
            "```",
            "",
        ])

    report_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local checks and write a quality report.")
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT),
        help="Markdown report path. Defaults to reports/quality_report.md.",
    )
    parser.add_argument(
        "--idea",
        action="append",
        default=[],
        help="Iteration idea to include in the report. Can be repeated.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ideas = args.idea or [
        "Make Viking static resource initialization idempotent to stop index.json growth.",
        "Use resource-level URIs so directory listing and direct node lookup are reliable.",
        "Keep memory writes append-only while preventing same-second URI collisions.",
    ]

    results = [run_command(name, command) for name, command in build_checks()]
    write_report(Path(args.report), results, ideas)

    for result in results:
        print(f"{result.status}: {result.name}")
    print(f"Report written: {Path(args.report).resolve()}")
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
