"""
Integration test: run REGI's Inflow.autoAdjust (the calculation
`district-scripts/SWT/*` and the example at
`regi-headless/src/test/resources/.../examples/InflowCalc.py` call as
`inflow_calc.autoAdjust(officeId, locationId, startDate, useLimits,
freezeRain)`) against the seeded EUFA project, and compare the series it
writes to against a frozen "known good" reference.

See README.md ("Known-good reference series") for the seeding pattern this
follows, and regi_calc_support.py for the shared helpers.
"""

from datetime import datetime, timezone

import pytest

from regi_calc_support import assert_timeseries_matches, fetch_timeseries

pytestmark = pytest.mark.integration

OFFICE_ID = "SWT"
PROJECT_ID = "EUFA"
ADJUSTED_INFLOW_TS_ID = "EUFA.Flow-Res In.Ave.~1Day.1Day.Regi-Rev-Adjusted"
EXPECTED_TS_ID = "EUFA.Flow-Res In.Ave.~1Day.1Day.REGI-Test-Expected"
CALCULATION_START = datetime(2026, 6, 1, tzinfo=timezone.utc)
COMPARISON_WINDOW_START = datetime(2026, 6, 3, tzinfo=timezone.utc)
COMPARISON_WINDOW_END = datetime(2026, 6, 7, tzinfo=timezone.utc)


def test_auto_adjust_matches_known_good_inflow(run_regi_calculation, cwms_session):
    def calculate(registry):
        inflow_calc = registry.getCalculation(1.0, "Inflow")
        inflow_calc.autoAdjust(OFFICE_ID, PROJECT_ID, CALCULATION_START, False, False)

    run_regi_calculation(calculate)

    computed = fetch_timeseries(
        ADJUSTED_INFLOW_TS_ID, OFFICE_ID, COMPARISON_WINDOW_START, COMPARISON_WINDOW_END,
    )
    expected = fetch_timeseries(
        EXPECTED_TS_ID, OFFICE_ID, COMPARISON_WINDOW_START, COMPARISON_WINDOW_END,
    )

    assert expected, (
        f"No data found for {EXPECTED_TS_ID!r} in the comparison window -- "
        "the known-good reference series didn't seed correctly."
    )
    assert_timeseries_matches(computed, expected)
