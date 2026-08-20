"""
Shared helpers for tests that run a REGI calculation (via regi_python) against
the seeded CDA stack and check its output against a frozen "known good"
reference timeseries.

Pattern these tests follow
---------------------------
1. `docker-compose.yml` + `compose_files/regi-data/regi.yml` seed a real CDA
   instance with input data for one or more calculations (see the `cda_stack`
   fixture in conftest.py).
2. Alongside the inputs, `regi.yml` also seeds *reference* data: a
   timeseries matching what the calculation writes to,
   but tagged with the version token "REGI-Test-Expected".
   It is never written to by any calculation -- it exists purely as this
   test suite's frozen comparison target.
3. The test runs the real calculation (through regi_python/run_headless)
   against the seeded stack, fetches the timeseries the calculation wrote
   via cwms-python (`fetch_timeseries` below), and compares it against the
   "REGI-Test-Expected" series with `assert_timeseries_matches`.

See README.md ("Known-good reference series") for how to add a new
comparison case following this pattern.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Sequence

TimeseriesPoint = tuple[datetime, float, int]


def fetch_timeseries(
    ts_id: str,
    office_id: str,
    begin: datetime,
    end: datetime,
) -> list[TimeseriesPoint]:
    """
    Fetches a timeseries from CDA via cwms-python and returns it as a list of
    (timestamp, value, quality_code) tuples sorted by time.
    """
    import cwms

    data = cwms.get_timeseries(ts_id=ts_id, office_id=office_id, begin=begin, end=end)

    points = [
        (timestamp.to_pydatetime(), value, quality)
        for timestamp, value, quality in data.df[
            ["date-time", "value", "quality-code"]
        ].itertuples(index=False, name=None)
    ]
    points.sort(key=lambda point: point[0])
    return points


def assert_timeseries_matches(
    actual: Sequence[TimeseriesPoint],
    expected: Sequence[TimeseriesPoint],
    *,
    abs_tol: float = 1e-6,
    rel_tol: float = 1e-6,
) -> None:
    """
    Asserts every timestamp in `expected` (the frozen "Test-Expected"
    reference series) is present in `actual` (freshly computed and fetched
    from CDA) with a matching value, within floating-point tolerance.

    `actual` may cover a wider time range than `expected` (e.g. because the
    calculation recomputed more of its period of record than just the
    comparison window); only timestamps present in `expected` are checked.
    """
    actual_by_time = {timestamp: value for timestamp, value, _ in actual}

    missing = [timestamp for timestamp, _, _ in expected if timestamp not in actual_by_time]
    mismatches = [
        (timestamp, actual_by_time[timestamp], expected_value)
        for timestamp, expected_value, _ in expected
        if timestamp in actual_by_time
        and not math.isclose(actual_by_time[timestamp], expected_value, rel_tol=rel_tol, abs_tol=abs_tol)
    ]

    if not missing and not mismatches:
        return

    lines = []
    if missing:
        lines.append(
            f"{len(missing)} expected timestamp(s) missing from computed output: "
            + ", ".join(timestamp.isoformat() for timestamp in missing)
        )
    if mismatches:
        lines.append(f"{len(mismatches)} value mismatch(es) (time: actual != expected):")
        lines.extend(
            f"  {timestamp.isoformat()}: {actual_value!r} != {expected_value!r}"
            for timestamp, actual_value, expected_value in mismatches
        )

    raise AssertionError("\n".join(lines))
