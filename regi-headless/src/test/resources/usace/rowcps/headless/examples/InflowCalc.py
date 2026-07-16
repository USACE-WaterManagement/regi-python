from regi_python import regi_session, run_headless


def calculate_inflow(registry):
    # Java imports must happen after regi_session starts the JVM.
    from java.util import Calendar, TimeZone

    # this gets a scriptable Pool Percent object
    inflow_calc = registry.getCalculation(1.0, "Inflow")

    # Time zone must be set because the Solaris time zone is UTC
    time_zone = TimeZone.getTimeZone("US/Central")
    # configure the start calendar
    start_cal = Calendar.getInstance(time_zone)
    start_cal.clear()
    start_cal.set(Calendar.YEAR, 2015)
    start_cal.set(Calendar.MONTH, 4)

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
    inflow_calc.autoAdjust("SWF", "ALAT2", start_cal.getTime(), False, False)


if __name__ == "__main__":
    with regi_session():
        run_headless(calculate_inflow)
