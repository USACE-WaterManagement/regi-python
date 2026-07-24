#!/usr/bin/env python3
"""Render a Cobertura-style coverage.xml (as produced by `coverage xml` /
pytest-cov's --cov-report=xml) as Markdown suitable for a GitHub Actions job
summary.

Usage:
    python3 python_coverage_summary.py <path-to-coverage.xml>

Prints to stdout; the caller is expected to redirect into $GITHUB_STEP_SUMMARY.
Deliberately has no third-party dependencies so it can run with the stock
`python3` already available on GitHub-hosted runners -- no extra permissions
or installs are needed, which keeps it safe to run on pull requests from
forks.
"""

import sys
import xml.etree.ElementTree as ET


def _pct(rate_attr):
    try:
        return float(rate_attr) * 100
    except (TypeError, ValueError):
        return 0.0


def main(argv):
    if len(argv) != 2:
        print("Usage: python_coverage_summary.py <coverage.xml>", file=sys.stderr)
        return 2

    path = argv[1]

    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        print("## Python test coverage")
        print()
        print(f"No coverage report found at `{path}` ({exc}).")
        return 0

    line_rate = _pct(root.get("line-rate"))
    branch_rate = _pct(root.get("branch-rate"))
    lines_covered = root.get("lines-covered", "?")
    lines_valid = root.get("lines-valid", "?")

    print("## Python test coverage")
    print()
    print(
        f"**Overall line coverage: {line_rate:.1f}%** "
        f"({lines_covered}/{lines_valid} lines) &nbsp;|&nbsp; "
        f"branch coverage: {branch_rate:.1f}%"
    )
    print()
    print("<details><summary>Per-file coverage</summary>")
    print()
    print("| File | Line coverage | Lines covered |")
    print("| --- | --- | --- |")

    classes = sorted(root.iter("class"), key=lambda c: c.get("filename", ""))
    for cls in classes:
        filename = cls.get("filename", "?")
        file_line_rate = _pct(cls.get("line-rate"))

        total = covered = 0
        lines_elem = cls.find("lines")
        if lines_elem is not None:
            for line in lines_elem.findall("line"):
                total += 1
                if int(line.get("hits", "0")) > 0:
                    covered += 1

        print(f"| `{filename}` | {file_line_rate:.1f}% | {covered}/{total} |")

    print()
    print("</details>")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
