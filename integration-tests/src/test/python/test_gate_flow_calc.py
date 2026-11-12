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
  - EUFA's Uncontrolled_Total is not tested: its CLOB's `<time_series_set>`
    is empty (`compose_files/regi-data/SWT/Clobs/FLOW.EUFA.UNCONTROLLED_TOTAL.json`)
    and EUFA has no uncontrolled-spillway rating (unlike FCOB's
    `FCOB.Elev;Flow-Uncontrolled_Spillway...`), so `computeFlowGroup` has
    nothing to write. FCOB's Uncontrolled_Total is covered instead.
"""

from datetime import datetime, timezone

import pytest

from regi_calc_support import assert_timeseries_matches, clear_timeseries, fetch_timeseries

pytestmark = pytest.mark.integration

OFFICE_ID = "SWT"
CALCULATION_START = datetime(2026, 6, 1, tzinfo=timezone.utc)
COMPARISON_WINDOW_START = datetime(2026, 6, 3, tzinfo=timezone.utc)
COMPARISON_WINDOW_END = datetime(2026, 6, 7, tzinfo=timezone.utc)

# Each FLOW_GROUPS entry defaults to the EUFA project and the June 1 -> June 3..7
# window above; a case for another project overrides `project_id` (and, if the
# project's data needs a different window, `calculation_start`/`window_start`/
# `window_end`).

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
    "FCOB_Uncontrolled_Total": {
        "project_id": "FCOB",
        "flow_group_name": "Flow.FCOB.Uncontrolled_Total",
        # CLOB attribute 0 is Inst 1Hour (not seeded); attribute 1 is the Ave
        # 1Hour series. FCOB's real 2026 pool (max ~1342.3 ft) never reaches the
        # uncontrolled spillway crest (1354.8 ft in
        # FCOB.Elev;Flow-Uncontrolled_Spillway), so FCOB.Elev.Inst.1Hour.0.Ccp-Rev
        # is SYNTHETIC for 2026-06-04..06-06: it holds 1355.0 / 1356.0 / 1356.5 ft
        # (exact points on the 2013 rating) for one day each. The expected series
        # is computed independently from those elevations and the rating
        # (23.2450894 / 341.631648 / 576.049241 cfs); each hour is the mean of
        # the flows at its start and end, so the day-boundary hours are halfway.
        "output_ts_id": "FCOB.Flow-Uncontrolled.Ave.1Hour.1Hour.Rev-Regi-Flowgroup",
        "expected_ts_id": "FCOB.Flow-Uncontrolled.Ave.1Hour.1Hour.REGI-Test-Expected",
    },
    "KEYS_TainterGate_Total": {
        "project_id": "KEYS",
        "flow_group_name": "Flow.KEYS.TainterGate_Total",
        # Output version is "regi" (not Rev-Regi-Flowgroup) per this CLOB.
        # KEYS' gate-change history starts 2026-06-22 21:00, so the window
        # sits after it where the tainter gates are open.
        "output_ts_id": "KEYS.Flow-RES-TGs.Ave.1Hour.1Hour.regi",
        "expected_ts_id": "KEYS.Flow-RES-TGs.Ave.1Hour.1Hour.REGI-Test-Expected",
        "calculation_start": datetime(2026, 6, 24, tzinfo=timezone.utc),
        "window_start": datetime(2026, 6, 25, tzinfo=timezone.utc),
        "window_end": datetime(2026, 6, 29, tzinfo=timezone.utc),
    },
}


@pytest.mark.parametrize("flow_group", FLOW_GROUPS.values(), ids=FLOW_GROUPS.keys())
def test_flow_group_matches_known_good_output(run_regi_calculation, cwms_session, flow_group):
    project_id = flow_group.get("project_id", "EUFA")
    calculation_start = flow_group.get("calculation_start", CALCULATION_START)
    window_start = flow_group.get("window_start", COMPARISON_WINDOW_START)
    window_end = flow_group.get("window_end", COMPARISON_WINDOW_END)

    clear_timeseries(flow_group["output_ts_id"], OFFICE_ID, window_start, window_end)

    def calculate(registry):
        gate_flow_calc = registry.getCalculation(1.0, "Gate Flow")
        gate_flow_calc.computeFlowGroup(
            OFFICE_ID, project_id, calculation_start, window_end,
            flow_group["flow_group_name"],
        )

    run_regi_calculation(calculate)

    computed = fetch_timeseries(
        flow_group["output_ts_id"], OFFICE_ID, window_start, window_end,
    )
    expected = fetch_timeseries(
        flow_group["expected_ts_id"], OFFICE_ID, window_start, window_end,
    )

    assert expected, (
        f"No data found for {flow_group['expected_ts_id']!r} in the comparison "
        "window -- the known-good reference series didn't seed correctly."
    )
    assert_timeseries_matches(computed, expected)
