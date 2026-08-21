from regi_python import regi_session, run_headless


def calculate_inflow(registry):
    # Java imports must happen after regi_session starts the JVM.
    from java.util import Calendar, TimeZone

    # this gets a ScriptableInflow instance.
    inflow_calc = registry.getCalculation(1.0, "Inflow")

    # configure the start calendar
    start_cal = Calendar.getInstance(TimeZone.getTimeZone("US/Central"))
    start_cal.clear()
    start_cal.set(Calendar.YEAR, 2018)
    start_cal.set(Calendar.MONTH, 7)

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
    inflow_calc.zeroNegatives("SWF", "ALAT2", start_cal.getTime())


if __name__ == "__main__":
    with regi_session():
        run_headless(calculate_inflow)
