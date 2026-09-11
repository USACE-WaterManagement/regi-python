"""
Integration test (scaffolded, still skipped): REGI's Gate Settings calculation.

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

Still blocked on two things, which is why this stays skipped:
  1. `EUFA.Opening.Inst.0.0.MANUAL` (the calc's input) has no seeded point
     data -- `regi.yml` lists the ts id so CDA knows about it, but nothing
     stages values for it, so the calc has no input to act on yet.
  2. EUFA's only seeded gate-change history (`GateChanges/EUFA.json`) falls
     in mid/late July 2026, not the June 2026 window every other calculation
     test here uses, so there's no historical output to freeze the same way
     `test_inflow_calc.py`/`test_gate_flow_calc.py` did.

To unskip: seed `EUFA.Opening.Inst.0.0.MANUAL` with real values for the
calculation window (per outlet under test), confirm what gate-change record
`createGateSettingsOutlet` actually produces from it, and freeze that as the
comparison target below.
"""

from datetime import datetime, timezone

import pytest

pytestmark = [
    pytest.mark.integration,
]

OFFICE_ID = "SWT"
PROJECT_ID = "EUFA"
CALCULATION_START = datetime(2026, 6, 1, tzinfo=timezone.utc)
CALCULATION_END = datetime(2026, 6, 7, tzinfo=timezone.utc)

# Expected opening (ft) per outlet, once EUFA.Opening.Inst.0.0.MANUAL is seeded
# and a real run's output has been verified and frozen here.
EXPECTED_OPENINGS_BY_OUTLET = {
    "EUFA-SG1": None,
    "EUFA-TG1": None,
}


@pytest.mark.parametrize("outlet_name", ["EUFA-SG1", "EUFA-TG1"])
def test_gate_settings_matches_known_good_opening(run_regi_calculation, cwms_session, outlet_name):
    import cwms

    def calculate(registry):
        gate_settings_calc = registry.getCalculation(1.0, "Gate Settings")
        gate_settings_calc.createGateSettingsOutlet(
            OFFICE_ID, PROJECT_ID, CALCULATION_START, CALCULATION_END, outlet_name
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
    assert openings[-1] == pytest.approx(expected_opening)
