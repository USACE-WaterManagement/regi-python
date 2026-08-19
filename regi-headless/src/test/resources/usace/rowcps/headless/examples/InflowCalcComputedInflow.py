from regi_python import regi_session, run_headless


def calculate_inflow(registry):
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo


    # this gets a ScriptableInflow instance.
    inflow_calc = registry.getCalculation(1.0, "Inflow")

    # Time zone must be set explicitly because the JVM's default timezone is
    # UTC, not the district's local time.
    central = ZoneInfo("America/Chicago")
    # Java's Calendar.MONTH was 0-indexed (4 == May); datetime.month is
    # 1-indexed, so we use 5 here for the same date.
    start_date = (datetime(2018, 5, 1, tzinfo=central)).astimezone(timezone.utc)
    end_date = (datetime(2018, 5, 4, tzinfo=central)).astimezone(timezone.utc)

    # This computes and saves inflow for EUFA in May 2018 given the computation options set above
    inflow_calc.computeInflow("SWT", "EUFA", start_date, end_date)


if __name__ == "__main__":
    with regi_session():
        run_headless(calculate_inflow)
