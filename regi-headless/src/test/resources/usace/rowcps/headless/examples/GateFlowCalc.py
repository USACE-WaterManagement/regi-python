import os.path
import sys

from regi_python import regi_session, run_headless


def calculate_gate_flow(registry):
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo

    # Java imports must happen after regi_session starts the JVM.
    from java.lang import System


    print("Now executing GateFlowCalc.py")
    print("os.arch:", System.getProperty("os.arch"))
    print("sys.path", sys.path)
    print("Working dir:", os.path.abspath("."))
    print("Library path:", System.getProperty("java.library.path"))

    sys.stdout.flush()

    gate_calc = registry.getCalculation(1.0, "Gate Flow")

    office_id = "SWF"
    project_id = "LEWT2"
    flow_group_id = "Flow.LEWT2.ConduitGate_Total"

    # Time zone must be set explicitly because the JVM's default timezone is
    # UTC, not the district's local time.
    central = ZoneInfo("America/Chicago")
    # Java's Calendar.MONTH was 0-indexed (1 == February); datetime.month is
    # 1-indexed, so we use 2 here for the same dates.
    start_date = (datetime(2015, 2, 1, tzinfo=central)).astimezone(timezone.utc)
    end_date = (datetime(2013, 2, 1, tzinfo=central)).astimezone(timezone.utc)

    gate_calc.computeFlowGroup(
        office_id,
        project_id,
        start_date,
        end_date,
        flow_group_id,
    )


if __name__ == "__main__":
    with regi_session():
        run_headless(calculate_gate_flow)
