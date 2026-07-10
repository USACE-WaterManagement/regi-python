import os.path
import sys

from regi_python import regi_session, run_headless


def calculate_gate_flow(registry):
    # Java imports must happen after regi_session starts the JVM.
    from java.lang import System
    from java.util import Calendar, TimeZone

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

    # Time zone must be set because the Solaris time zone is UTC
    time_zone = TimeZone.getTimeZone("US/Central")
    start_cal = Calendar.getInstance(time_zone)
    start_cal.clear()
    start_cal.set(Calendar.YEAR, 2015)
    start_cal.set(Calendar.MONTH, 1)

    end_cal = Calendar.getInstance(time_zone)
    end_cal.clear()
    end_cal.set(Calendar.YEAR, 2013)
    end_cal.set(Calendar.MONTH, 1)

    gate_calc.computeFlowGroup(
        office_id,
        project_id,
        start_cal.getTimeInMillis(),
        end_cal.getTimeInMillis(),
        flow_group_id,
    )


if __name__ == "__main__":
    with regi_session():
        run_headless(calculate_gate_flow)
