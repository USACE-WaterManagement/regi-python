"""
Integration tests: REGI's daily Inflow calculation against the seeded EUFA
project, run the way the district scripts run it (see
`district-scripts/SWL/Big3-InflowCalcMultipleActions.py`):

    computeInflow(office, project, start, end)
    cloneInflows(office, project, start)
    autoAdjust(office, project, start, useLimits, freezeRain)

Two things about how REGI reads dates matter for these tests:

  - REGI keys its daily rows on *project-local midnight*. The Python-to-Java
    bridge only understands UTC datetimes (any other tzinfo is read as if its
    wall-clock fields were UTC), so, like the district scripts, the dates passed
    in are project-local midnights converted to UTC (`project_midnight`).
    Passing UTC midnight instead puts every row at 7pm local time and the
    calculation fails or writes rows off the daily grid.
  - A computed value stamped at local midnight K describes the day that ends at
    K, so the value at 2026-06-03T05:00Z (midnight CDT) is the inflow of June 2.

REGI reads the computed series (`Raw-Regi-Computed`) while it runs, and CDA
answers a read of an *empty* series with an error that REGI logs, so the seed
holds that series with a sentinel value of zero for every day of the month.
The tests do not clear it: a run that writes nothing leaves zeros, which do not
match the recorded values. The seeded production values of the adjusted
series (`Regi-Rev-Adjusted`) carry the protected quality bit, which stops REGI
overwriting them, so that series is cleared before the run (`clear_timeseries`
overrides the protection).

The seed overrides one association from the SWT property set:
`Regi_project_PRIMARY.Hourly_computed_inflow_daily` carries a `~0s` suffix
(`...~1Day~0s.1Day.Raw-Regi-Computed`). The suffix is REGI-only notation, not
part of the CDA time series id: it tells REGI the series is local-regular with
a zero offset. Without it, REGI derives a bogus offset (-3h14m7s) for the
output series and writes rows off the grid.
"""

import math
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from regi_calc_support import clear_timeseries, fetch_timeseries

pytestmark = pytest.mark.integration

OFFICE_ID = "SWT"
PROJECT_ID = "EUFA"
PROJECT_TIME_ZONE = ZoneInfo("America/Chicago")

COMPUTED_TS_ID = "EUFA.Flow-Res In.Ave.~1Day.1Day.Raw-Regi-Computed"
ADJUSTED_TS_ID = "EUFA.Flow-Res In.Ave.~1Day.1Day.Regi-Rev-Adjusted"

# REGI's computed daily inflow (cfs) for the day ending at project-local midnight
# of each date below (June 2026), from the seeded EUFA data. These were checked
# once against an independent calculation (storage change + average release +
# 0.7 x evaporation volume, within 150 cfs per day) and then recorded. The seed
# is fixed, so any change here is a change in REGI's calculation.
EXPECTED_COMPUTED_INFLOW = {
    date(2026, 6, 3): 2624.0292865766,
    date(2026, 6, 4): 3675.9514236595,
    date(2026, 6, 5): 301.6483822784,
    date(2026, 6, 6): 1000.6048425474,
    date(2026, 6, 7): 21274.7255524624,
    date(2026, 6, 8): 11321.7382125349,
    date(2026, 6, 9): 8915.5846164727,
    date(2026, 6, 10): 6992.8995714082,
    date(2026, 6, 11): 3913.7061393013,
    date(2026, 6, 12): 2303.1533234863,
    date(2026, 6, 13): 28013.2758212625,
    date(2026, 6, 14): 9363.3830035496,
    date(2026, 6, 15): 16430.2038722679,
    date(2026, 6, 16): 8745.2876986413,
    date(2026, 6, 17): 3780.8088021152,
    date(2026, 6, 18): 2079.0075747677,
    date(2026, 6, 19): 4289.5905872626,
    date(2026, 6, 20): -184.3313279051,
    date(2026, 6, 21): 3866.6160894845,
}


def project_midnight(year: int, month: int, day: int) -> datetime:
    """Project-local midnight, as the UTC datetime REGI's Python bridge expects."""
    return datetime(year, month, day, tzinfo=PROJECT_TIME_ZONE).astimezone(timezone.utc)


MONTH_START = project_midnight(2026, 6, 1)
MONTH_END = project_midnight(2026, 7, 1)

def test_compute_inflow_matches_expected_values(run_regi_calculation, cwms_session):
    def calculate(registry):
        inflow_calc = registry.getCalculation(1.0, "Inflow")
        inflow_calc.computeInflow(OFFICE_ID, PROJECT_ID, MONTH_START, MONTH_END)

    run_regi_calculation(calculate)

    first, last = min(EXPECTED_COMPUTED_INFLOW), max(EXPECTED_COMPUTED_INFLOW)
    computed = _values(
        COMPUTED_TS_ID,
        project_midnight(first.year, first.month, first.day),
        project_midnight(last.year, last.month, last.day),
    )
    actual = {time.astimezone(PROJECT_TIME_ZONE).date(): value for time, value in computed.items()}
    misses = [
        f"  {day}: REGI {actual.get(day)} vs expected {expected}"
        for day, expected in EXPECTED_COMPUTED_INFLOW.items()
        if actual.get(day) != pytest.approx(expected, rel=1e-6)
    ]
    assert not misses, "Computed inflow differs from the recorded values (cfs):\n" + "\n".join(misses)
    assert set(actual) == set(EXPECTED_COMPUTED_INFLOW), (
        f"Unexpected days in the computed window: {sorted(set(actual) - set(EXPECTED_COMPUTED_INFLOW))}"
    )


def test_auto_adjust_conserves_computed_volume(run_regi_calculation, cwms_session):
    clear_timeseries(ADJUSTED_TS_ID, OFFICE_ID, MONTH_START, MONTH_END)

    def calculate(registry):
        inflow_calc = registry.getCalculation(1.0, "Inflow")
        inflow_calc.computeInflow(OFFICE_ID, PROJECT_ID, MONTH_START, MONTH_END)
        inflow_calc.cloneInflows(OFFICE_ID, PROJECT_ID, MONTH_START)
        inflow_calc.autoAdjust(OFFICE_ID, PROJECT_ID, MONTH_START, False, False)

    run_regi_calculation(calculate)

    computed = _values(COMPUTED_TS_ID, MONTH_START, MONTH_END)
    adjusted = _values(ADJUSTED_TS_ID, MONTH_START, MONTH_END)
    assert computed, "REGI wrote no computed inflow for the month."
    assert set(adjusted) == set(computed), (
        "Adjusted and computed inflow cover different days: "
        f"only computed {sorted(set(computed) - set(adjusted))}, only adjusted {sorted(set(adjusted) - set(computed))}"
    )

    # Auto Adjust keeps the month's total volume equal to the computed total...
    assert math.isclose(sum(adjusted.values()), sum(computed.values()), rel_tol=1e-9), (
        f"Adjusted total {sum(adjusted.values())} != computed total {sum(computed.values())}"
    )
    # ...removes zero and negative days...
    assert all(value > 0 for value in adjusted.values()), (
        "Adjusted inflow still has non-positive days: "
        + ", ".join(f"{day.isoformat()}={value}" for day, value in sorted(adjusted.items()) if value <= 0)
    )
    # ...and scales every day that was already positive by one common factor.
    ratios = [adjusted[day] / computed[day] for day in computed if computed[day] > 0]
    assert ratios, "No positive computed days to compare."
    assert max(ratios) - min(ratios) < 1e-9, (
        f"Positive days were not scaled by a common factor: ratios span {min(ratios)} .. {max(ratios)}"
    )


def _values(ts_id: str, begin: datetime, end: datetime) -> dict[datetime, float]:
    return {time: value for time, value, _ in fetch_timeseries(ts_id, OFFICE_ID, begin, end)}
