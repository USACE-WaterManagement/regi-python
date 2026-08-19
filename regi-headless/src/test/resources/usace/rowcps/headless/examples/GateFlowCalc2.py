from regi_python import regi_session, run_headless


def calculate_gate_flow(registry):
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo


    names = registry.getNames(1.0)
    print("names", names)

    gate_calc = registry.getCalculation(1.0, "Gate Flow")

    # Time zone must be set explicitly because the JVM's default timezone is
    # UTC, not the district's local time.
    central = ZoneInfo("America/Chicago")
    # Java's Calendar.MONTH was 0-indexed (4 == May, 6 == July); datetime.month
    # is 1-indexed, so we use 5 and 7 here for the same dates.
    start_date = (datetime(2015, 5, 1, tzinfo=central)).astimezone(timezone.utc)
    end_date = (datetime(2015, 7, 1, tzinfo=central)).astimezone(timezone.utc)

    gate_calc.computeAll("SWF", "LEWT2", start_date, end_date)


if __name__ == "__main__":
    with regi_session():
        run_headless(calculate_gate_flow)
