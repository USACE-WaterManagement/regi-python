"""
Integration test: run REGI's Gate Flow calculation (`computeFlowGroup`) against
each of EUFA's seeded flow groups, and compare the series it writes to against
a frozen "known good" reference.

See README.md ("Known-good reference series") for the seeding pattern this
follows, and regi_calc_support.py for the shared helpers.

Output ts id: `computeFlowGroup` writes through
`usace.rowcps.computation.flowgroup.DbCommitFlowGroupCalc` (not vendored in
this repo -- compiled dependency only), which resolves its output ts id(s)
from the flow group's own definition rather than a fixed naming rule. Rather
than guess or require a live JVM run, each flow group's real output ts id(s)
were read directly out of its seeded CLOB
(`compose_files/regi-data/SWT/Clobs/FLOW.EUFA.<SUFFIX>.json`) -- the CLOB's
`<time_series_set>` lists every ts the calc writes to
(`save_to_database="true"` on each `<time_series_id>`), tagged with an
`attribute` ordinal. `attribute="0"` is treated here as the primary output,
matching Project_Total's CLOB (attribute 0 = the `~1Day` daily average,
which is also the one that already had real seeded values, confirming this
reading is correct) -- see FLOW_GROUPS below for the other candidate ts ids
each CLOB lists, in case a different one turns out to be the right target.

Not every flow group is testable:
  - Project_Total, Gated_Total, Turbine_Total: all fully testable -- each
    CLOB's attribute-0 output ts (`EUFA.Flow-Res Out...`/
    `EUFA.Flow-Controlled...`/`EUFA.Flow-Power...`) already has real point
    data seeded for the June 2026 comparison window, frozen into its own
    REGI-Test-Expected reference the same way (see "Known-good reference
    series" in README.md). Gated_Total's window happens to be all zero
    (gates were closed that week) -- that's real seeded history, not a
    placeholder.
  - Uncontrolled_Total: its CLOB's `<time_series_set>` is empty
    (`compose_files/regi-data/SWT/Clobs/FLOW.EUFA.UNCONTROLLED_TOTAL.json`)
    -- no output ts is configured for this flow group at all. Unlike the
    other three, this isn't a seeding gap: EUFA has no uncontrolled-spillway
    structure (no rating for one, unlike e.g. FCOB's
    `FCOB.Elev;Flow-Uncontrolled_Spillway...` rating), so `computeFlowGroup`
    genuinely has nothing to write here. Stays skipped for that reason.
"""

from datetime import datetime, timezone

import pytest

from regi_calc_support import assert_timeseries_matches, fetch_timeseries

pytestmark = pytest.mark.integration

OFFICE_ID = "SWT"
PROJECT_ID = "EUFA"
CALCULATION_START = datetime(2026, 6, 1, tzinfo=timezone.utc)
COMPARISON_WINDOW_START = datetime(2026, 6, 3, tzinfo=timezone.utc)
COMPARISON_WINDOW_END = datetime(2026, 6, 7, tzinfo=timezone.utc)

FLOW_GROUPS = {
    "Project_Total": {
        "flow_group_name": "Flow.EUFA.Project_Total",
        # Other candidates from the CLOB: Flow-Res Out.Ave.1Hour.1Hour and
        # Flow-Res Out.Inst.1Hour.0 (both also version Rev-Regi-Flowgroup).
        "output_ts_id": "EUFA.Flow-Res Out.Ave.~1Day.1Day.Rev-Regi-Flowgroup",
        "expected_ts_id": "EUFA.Flow-Res Out.Ave.~1Day.1Day.REGI-Test-Expected",
    },
    "Gated_Total": {
        "flow_group_name": "Flow.EUFA.Gated_Total",
        # Other candidate from the CLOB: Flow-Controlled.Inst.1Hour.0.
        "output_ts_id": "EUFA.Flow-Controlled.Ave.1Hour.1Hour.Rev-Regi-Flowgroup",
        "expected_ts_id": "EUFA.Flow-Controlled.Ave.1Hour.1Hour.REGI-Test-Expected",
    },
    "Turbine_Total": {
        "flow_group_name": "Flow.EUFA.Turbine_Total",
        # The CLOB's attribute ordinals put the 1Hour average first
        # (attribute 0) here, unlike Project_Total/Gated_Total where the
        # coarser interval is attribute 0 -- worth double-checking once a
        # live run is possible. Other candidates: Flow-Power.Ave.~1Day.1Day
        # (attribute 2) and Flow-Power.Inst.1Hour.0 (attribute 1).
        "output_ts_id": "EUFA.Flow-Power.Ave.1Hour.1Hour.Rev-Regi-Flowgroup",
        "expected_ts_id": "EUFA.Flow-Power.Ave.1Hour.1Hour.REGI-Test-Expected",
    },
    "Uncontrolled_Total": pytest.param(
        {
            "flow_group_name": "Flow.EUFA.Uncontrolled_Total",
            "output_ts_id": None,
            "expected_ts_id": None,
        },
        marks=pytest.mark.skip(
            reason="FLOW.EUFA.UNCONTROLLED_TOTAL's CLOB has an empty "
            "<time_series_set/> -- no output ts is configured for this flow "
            "group at all yet, so computeFlowGroup has nothing to write."
        ),
    ),
}


@pytest.mark.parametrize("flow_group", FLOW_GROUPS.values(), ids=FLOW_GROUPS.keys())
def test_flow_group_matches_known_good_output(run_regi_calculation, cwms_session, flow_group):
    def calculate(registry):
        gate_flow_calc = registry.getCalculation(1.0, "Gate Flow")
        gate_flow_calc.computeFlowGroup(
            OFFICE_ID, PROJECT_ID, CALCULATION_START, COMPARISON_WINDOW_END,
            flow_group["flow_group_name"],
        )

    run_regi_calculation(calculate)

    computed = fetch_timeseries(
        flow_group["output_ts_id"], OFFICE_ID, COMPARISON_WINDOW_START, COMPARISON_WINDOW_END,
    )
    expected = fetch_timeseries(
        flow_group["expected_ts_id"], OFFICE_ID, COMPARISON_WINDOW_START, COMPARISON_WINDOW_END,
    )

    assert expected, (
        f"No data found for {flow_group['expected_ts_id']!r} in the comparison "
        "window -- the known-good reference series didn't seed correctly."
    )
    assert_timeseries_matches(computed, expected)
