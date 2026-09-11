from regi_python import regi_session, run_headless


def calculate_inflow(registry):
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo


    # this gets a ScriptableInflow instance.
    inflow_calc = registry.getCalculation(1.0, "Inflow")

    # Time zone must be set explicitly because the JVM's default timezone is
    # UTC, not the district's local time.
    central = ZoneInfo("America/Chicago")
    # Java's Calendar.MONTH was 0-indexed (6 == July); datetime.month is
    # 1-indexed, so we use 7 here for the same date.
    start_date = (datetime(2018, 7, 1, tzinfo=central)).astimezone(timezone.utc)

    # inflow_calc contains 4 callable methods:
    # autoAdjust
    # balanceAll
    # cloneInflows
    # zeroNegatives

    # Each method takes the following arguments:
    #   officeId
    #   locationId
    #   startDate

    # autoAdjust also takes booleans:
    #   useLimits
    #   freezeRain

    # This autoBalances ALAT2
    inflow_calc.autoAdjust("SWF", "ALAT2", start_date, False, False)


if __name__ == "__main__":
    with regi_session():
        run_headless(calculate_inflow)
