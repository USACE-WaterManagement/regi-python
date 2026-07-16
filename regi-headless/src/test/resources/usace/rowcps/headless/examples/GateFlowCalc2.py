from regi_python import regi_session, run_headless


def calculate_gate_flow(registry):
    # Java imports must happen after regi_session starts the JVM.
    from java.util import Calendar, TimeZone

    names = registry.getNames(1.0)
    print("names", names)

    gate_calc = registry.getCalculation(1.0, "Gate Flow")

    # Time zone must be set because the Solaris time zone is UTC
    time_zone = TimeZone.getTimeZone("US/Central")
    start_cal = Calendar.getInstance(time_zone)
    start_cal.clear()
    start_cal.set(Calendar.YEAR, 2015)
    start_cal.set(Calendar.MONTH, 4)

    end_cal = Calendar.getInstance(time_zone)
    end_cal.clear()
    end_cal.set(Calendar.YEAR, 2015)
    end_cal.set(Calendar.MONTH, 6)

    gate_calc.computeAll("SWF", "LEWT2", start_cal.getTimeInMillis(), end_cal.getTimeInMillis())


if __name__ == "__main__":
    with regi_session():
        run_headless(calculate_gate_flow)
