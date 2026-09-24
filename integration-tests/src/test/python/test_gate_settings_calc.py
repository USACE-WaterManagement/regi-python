"""
Integration test (still skipped): REGI's Gate Settings calculation.

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

That fourth fix lives in a separate repo (`cwms-regi-tools`) and hasn't been
released/re-pinned into this repo's `mil.army.wmist.regi-tools` dependency
version yet, so it can't be exercised from here. This test stays skipped
until that version bump happens; at that point, re-running it should produce
a real gate-change write end-to-end -- confirm the actual opening values and
freeze them into `EXPECTED_OPENINGS_BY_OUTLET` below.
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

# Expected opening (ft) per outlet, keyed by CDA's fully-qualified location id,
# once a real run's output has been verified and frozen here.
EXPECTED_OPENINGS_BY_OUTLET = {
    "EUFA-SG1": None,
    "EUFA-TG1": None,
}


@pytest.mark.parametrize("outlet_sub_location", ["SG1", "TG1"])
def test_gate_settings_matches_known_good_opening(run_regi_calculation, cwms_session, outlet_sub_location):
    import cwms

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

    gate_changes = cwms.get_all_gate_changes(
        office_id=OFFICE_ID, project_id=PROJECT_ID, begin=CALCULATION_START, end=CALCULATION_END
    ).json

    openings = [
        setting["opening"]
        for change in gate_changes
        for setting in change.get("settings", [])
        if setting["location-id"]["name"] == outlet_name
    ]

    expected_opening = EXPECTED_OPENINGS_BY_OUTLET[outlet_name]
    assert openings, f"No gate-change settings found for {outlet_name!r} in the calculation window."
    if expected_opening is None:
        pytest.fail(f"DISCOVERY RUN -- observed openings for {outlet_name!r}: {openings!r}")
    assert openings[-1] == pytest.approx(expected_opening)
