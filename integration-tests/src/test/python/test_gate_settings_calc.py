"""
Integration test: REGI's Gate Settings calculation.

Unlike Inflow/Gate Flow, `createGateSettingsOutlet` does not write a plain
timeseries at all -- source inspection of `ScriptableGateSettingsImpl` (in
:regi-headless) shows it reads an *input* association ts (property
`Regi_gate_INPUT.GateSettings_gate_opening.<PROJECT>`, seeded here as
`EUFA.Opening.Inst.0.0.MANUAL` -- see
`compose_files/regi-data/SWT/Properties/LOCATION TIME SERIES ASSOCIATION.json`),
diffs it against the in-memory gate-opening cache, and persists real CWMS
*gate-change* records (`AtOutletManager`/`HeadlessGateCache.saveData`) -- the
same "gate-change" resource seeded under
`compose_files/regi-data/SWT/GateChanges/EUFA.json` and fetched here via
`cwms.get_all_gate_changes`. So the comparison target is a gate-change
record's per-outlet "opening" setting, not a "...Opening....REGI-Test-Expected"
timeseries (that placeholder in earlier versions of this test was never a
real output shape).

Getting an actual gate-change write out of `createGateSettingsOutlet` took
four real fixes, three landed here and one landed upstream:

1. `GateSettingsDataAdapter.getGateObjects()` (in `regi/computation`) builds
   its outlet-group container from CWMS **Rating**-category location groups.
   That assignment already existed in
   `compose_files/regi-data/SWT/LocationGroups/Rating.json` (`EUFA-SluiceGate`
   assigning `EUFA-SG1` to `EUFA.Opening-Sluice_Gates,Elev;Flow-Sluice_Gates.
   Standard.Production`, `EUFA-TainterGate` assigning `EUFA-TG1` etc. to the
   `Spillway_Gates` rating), but `regi.yml`'s (and `regi.generated.yml`'s)
   `locationGroups:` entries for those two ids were tagged `categoryId: Flow`
   instead of `categoryId: Rating`, so `cda-etl` never staged them into CDA
   under the Rating category. Fixed by correcting both entries' `categoryId`.
2. Even with the outlet groups resolving, `createGateSettingsOutlet` logged
   "Outlet does not exist" for `EUFA-SG1`/`EUFA-TG1`. Diagnostic logging in
   `getIControlledOutlet` showed `IControlledOutletGroupContainer.
   getOutletMap()` is keyed by each outlet's bare *sub-location* name (`SG1`,
   `TG1`), not CDA's fully-qualified id (`EUFA-SG1`). `createGateSettingsOutlet`
   must be called with the short form (`outlet_sub_location` below), while
   CDA's gate-change records still report the fully-qualified id in
   `settings[].location-id.name` -- the two are kept distinct here.
3. Two more fixes came from tracing `ScriptableGateSettingsImpl`'s real diff
   path (`createGateSettingsOutlet(gc, locRef, ..., tsIdStr, options)`):
   - The calculation window has to bracket EUFA's *real* gate-change history
     (`GateChanges/EUFA.json`: 2026-07-16 13:06, 2026-07-22 12:00, 2026-07-22
     15:17) -- specifically it must *start after* the first real record, or
     `GateCache`'s head-of-record lookback 404s the same way a plain June
     2026 window does (every other calc test's window). Narrowed to
     2026-07-17..07-22.
   - `getFirstTimeSeriesDescription` doesn't read the flat association ts
     (`EUFA.Opening.Inst.0.0.MANUAL`) directly -- `updateParameters()`
     rewrites the ts id per outlet using the Rating location group's own
     independent parameter name and the outlet's full location id, so the
     calc actually looks up `EUFA-SG1.Opening-Sluice_Gates.Inst.0.0.MANUAL`
     and `EUFA-TG1.Opening-Spillway_Gates.Inst.0.0.MANUAL`. Neither existed;
     seeded both under `compose_files/regi-data/SWT/Timeseries/` and
     registered them in `regi.yml`/`regi.generated.yml`. Confirmed working:
     the JVM log now shows "3 modifications were made to the gate settings"
     for both outlets, at exactly the seeded input timestamps.
4. With the outlet resolving and real modifications computed, `run_headless`'s
   final `regi_domain.commitData(manager_id)` still failed -- a 409
   `DataAlreadyExistsException` re-creating the already-existing `EUFA-SG1`
   outlet (`POST .../outlets?fail-if-exists=true`). Traced to a real bug in
   `cwms-regi-tools`: `PhysicalStructureManager.retrieveRatingGroups()` (in
   `regi-cache/regi-dao`) unconditionally calls `t.setRatingGroupRef(...)` on
   every freshly-retrieved outlet whenever its Rating-category group
   resolves, which marks the outlet "modified" even though nothing was
   actually edited -- `commitData()` then tries to re-create it. This only
   started firing *because* fix #1 made the Rating group resolve for the
   first time; before that, `locationGroups.isEmpty()` was true and the
   setter (and the bug) never ran. Fixed upstream in
   `cwms-regi-tools/regi-cache/regi-dao/.../PhysicalStructureManager.java`
   by preserving the outlet's pre-existing `isModified()` state across that
   read-time cache-sync call.

That fourth fix was released in `mil.army.wmist.regi-tools` 10.0.0 (pinned in
`gradle/libs.versions.toml`; the wheel bundles `regi-dao-10.0.0.jar`), so the
calculation now commits end-to-end.

Three more things this test has to handle:

- `cwms.get_all_gate_changes` / `cwms.delete_gate_change` default to
  `Accept: application/json;version=2`, which CDA's gate-changes endpoint
  rejects with a 406, so the calls below go through `cwms.api` with
  `api_version=1`. An empty window is a 404, treated as "no changes".
- The calculation persists real gate changes, and they survive between
  tests. Left in place, the SG1 changes made the TG1 run fail ("Gate changes
  are not in ascending time order"), and any leftover would let the assertion
  pass without the calculation having written anything. The `clean_window`
  fixture deletes every gate change in the calculation window before and after
  each test. EUFA's seeded changes (2026-07-16 13:06, 2026-07-22 12:00,
  2026-07-22 15:17) are all outside the window, so they stay as the lookback
  record the calculation needs, and everything observed in the window was
  written by the calculation.

Expected values are derived by hand from the seeded input timeseries
(`EUFA-SG1.Opening-Sluice_Gates.Inst.0.0.MANUAL`,
`EUFA-TG1.Opening-Spillway_Gates.Inst.0.0.MANUAL`), which both step at
2026-07-17 00:00Z, 2026-07-19 00:00Z and 2026-07-21 12:00Z -- the same three
dates REGI logs as "3 modifications were made to the gate settings". Only the
first two (the non-zero openings) are persisted; see EXPECTED_OPENINGS_BY_OUTLET.
"""

from datetime import datetime, timezone

import pytest

pytestmark = [
    pytest.mark.integration,
]

OFFICE_ID = "SWT"
PROJECT_ID = "EUFA"
CALCULATION_START = datetime(2026, 7, 17, tzinfo=timezone.utc)
CALCULATION_END = datetime(2026, 7, 22, tzinfo=timezone.utc)

# Opening (ft) per outlet at each gate change the calculation must write, keyed
# by the outlet's bare sub-location name and ordered by change date. Taken from
# the seeded input timeseries (see module docstring). The inputs also close the
# gate at 2026-07-21 12:00Z (0.0). REGI logs that as a third modification but
# never persists a gate change for it (checked against CDA: nothing stored
# between 07-19 and the seeded 07-22 12:00 "closed" record), so the closure is
# deliberately not listed -- if REGI starts persisting it, this test fails and
# the closure (a change with no setting for the outlet) should be added.
EXPECTED_OPENINGS_BY_OUTLET = {
    "SG1": [
        (datetime(2026, 7, 17, tzinfo=timezone.utc), 0.5),
        (datetime(2026, 7, 19, tzinfo=timezone.utc), 1.2),
    ],
    "TG1": [
        (datetime(2026, 7, 17, tzinfo=timezone.utc), 1.0),
        (datetime(2026, 7, 19, tzinfo=timezone.utc), 3.5),
    ],
}


def _gate_changes_endpoint():
    return f"projects/{OFFICE_ID}/{PROJECT_ID}/gate-changes"


def _window_params(**extra):
    return {
        "begin": CALCULATION_START.isoformat(),
        "end": CALCULATION_END.isoformat(),
        **extra,
    }


def _get_gate_changes_in_window():
    from cwms import api

    try:
        return api.get(
            _gate_changes_endpoint(),
            params=_window_params(
                **{"start-time-inclusive": True, "end-time-inclusive": False, "unit-system": "EN"}
            ),
            api_version=1,
        )
    except api.ApiError as error:
        if error.response.status_code == 404:  # CDA's answer for an empty window
            return []
        raise


def _delete_gate_changes_in_window():
    from cwms import api

    try:
        api.delete(
            _gate_changes_endpoint(),
            params=_window_params(**{"override-protection": True}),
            api_version=1,
        )
    except api.ApiError as error:
        if error.response.status_code != 404:
            raise


@pytest.fixture
def clean_window(cwms_session):
    """No gate changes in the calculation window before or after the test."""
    _delete_gate_changes_in_window()
    assert not _get_gate_changes_in_window(), "Could not clear the calculation window."
    yield
    _delete_gate_changes_in_window()


@pytest.mark.parametrize("outlet_sub_location", ["SG1", "TG1"])
def test_gate_settings_matches_known_good_opening(run_regi_calculation, clean_window, outlet_sub_location):
    outlet_name = f"{PROJECT_ID}-{outlet_sub_location}"

    def calculate(registry):
        gate_settings_calc = registry.getCalculation(1.0, "Gate Settings")
        # createGateSettingsOutlet's outletId must be the bare sub-location
        # name (e.g. "SG1") -- the outlet-group container it looks the
        # outlet up in is keyed that way, not by the fully-qualified CDA
        # location id ("EUFA-SG1"). See module docstring.
        gate_settings_calc.createGateSettingsOutlet(
            OFFICE_ID, PROJECT_ID, CALCULATION_START, CALCULATION_END, outlet_sub_location
        )

    run_regi_calculation(calculate)

    # The window was empty before the run, so every change here was written by
    # the calculation. Each change reports this outlet's opening, or None when
    # it carries no setting for it.
    observed_openings = []
    for change in _get_gate_changes_in_window():
        openings = [
            setting["opening"]
            for setting in change.get("settings", [])
            if setting["location-id"]["name"] == outlet_name
        ]
        assert len(openings) <= 1, f"Several {outlet_name!r} settings in one gate change: {openings!r}"
        observed_openings.append(
            (
                datetime.fromtimestamp(change["change-date"] / 1000, tz=timezone.utc),
                openings[0] if openings else None,
            )
        )

    assert observed_openings == [
        (when, None if opening is None else pytest.approx(opening))
        for when, opening in EXPECTED_OPENINGS_BY_OUTLET[outlet_sub_location]
    ]
