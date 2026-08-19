from regi_python import regi_session, run_headless


def run_calculations(registry):
    from datetime import datetime, timedelta, timezone
    from zoneinfo import ZoneInfo

    # Java imports must happen after regi_session starts the JVM.
    from usace.rowcps.headless import LoggingOptions


    # Description of: LoggingOptions.setDbMessageLevel(int level)
    #
    # Adds Time Series logging messages in the OracleTimeSeriesDaoImpl.  Recommended
    # level is 2, as this provides basic information about the time series
    # retrieval/storage.
    #
    # Message Level | Description
    # --------------|-------------------------------------------------------------------------------------------------------------------------------|
    # <=0           | Default value, does not do anything.  Lower values do not change behavior.                                                  |
    # 1             | Logs message when no data is found.  Logs message when data is found, how much was retrieved or stored, and how long it took. |
    # 2             | Adds message with name of time series, and the units to retrieve/store.                                                       |
    # 3             | Adds message with the current time.                                                                                           |
    # 4             | Adds message with first 10 dates and values from each time series.                                                            |
    # >4            | Same as 4, but shows all values retrieved from each time series.  Higher values do not change behavior.                       |
    # --------------|-------------------------------------------------------------------------------------------------------------------------------|

    LoggingOptions.setDbMessageLevel(2)


    # Description of: LoggingOptions.setMetricsEnabled(boolean value)
    #
    # Enables or disables the storage of REGI's Metric data pertaining to the
    # performance of the application.  This is incredibly helpful for identifying
    # issues where the application takes an excessive amount of time to operate.
    #
    # Metrics also log the location of the files as an INFO message if they are
    # enabled.
    #
    # By default, Metrics are disabled.

    # LoggingOptions.setMetricsEnabled(True)

    # this gets a scriptable Pool Percent object
    inflowCalc = registry.getCalculation(1.0, "Inflow")

    # Time zone must be set explicitly because the JVM's default timezone is
    # UTC, not the district's local time.
    central = ZoneInfo("America/Chicago")
    today_midnight = datetime.now(central).replace(hour=0, minute=0, second=0, microsecond=0)

    officeID = "SWL"
    # start: 7 days ago, at midnight
    startDate = (today_midnight - timedelta(days=7)).astimezone(timezone.utc)
    # end: tomorrow, at midnight
    endDate = (today_midnight + timedelta(days=1)).astimezone(timezone.utc)

    # inflowCalc contains 4 callable methods:
    # autoAdjust
    # balanceAll
    # cloneInflows
    # zeroNegatives

    # Each method takes the following arguments:
    #   officeId
    #   locationId
    #   startDate

    # autoAdjust also takes booleans:
    #    useLimits
    #    freezeRain

    # UseLimits and FreezeRain are also controllable arguments for AutoAdjust. By setting "useLimits_ON" to True,
    # the function will use the "useLimits command. By setting it to "False", it will be turned off. This functions the same way for "freezeRain_ON"
    # If the Auto Adjust command is not used, these arguments will have no influence on the other commands.
    useLimits_ON = True
    freezeRain_ON = True

    # Commands are a dict of location -> list of (method, extra_args)
    # pairs to run there, in order. `method` is the real inflowCalc method
    # reference; `extra_args` is whatever it needs after (officeID,
    # location). Locations/actions can be commented out or removed as
    # needed.
    actions = {
        "Beaver_Dam": [
            (inflowCalc.computeInflow, (startDate, endDate)),
            (inflowCalc.cloneInflows, (startDate,)),
            (inflowCalc.autoAdjust, (startDate, useLimits_ON, freezeRain_ON)),
        ],
        "Table_Rock_Dam": [
            (inflowCalc.computeInflow, (startDate, endDate)),
            (inflowCalc.cloneInflows, (startDate,)),
            (inflowCalc.autoAdjust, (startDate, useLimits_ON, freezeRain_ON)),
        ],
        "Bull_Shoals_Dam": [
            (inflowCalc.computeInflow, (startDate, endDate)),
            (inflowCalc.cloneInflows, (startDate,)),
            (inflowCalc.autoAdjust, (startDate, useLimits_ON, freezeRain_ON)),
        ],
        "Norfork_Dam": [
            (inflowCalc.computeInflow, (startDate, endDate)),
            (inflowCalc.cloneInflows, (startDate,)),
            (inflowCalc.autoAdjust, (startDate, useLimits_ON, freezeRain_ON)),
        ],
        "GreersFerry_Dam": [
            (inflowCalc.computeInflow, (startDate, endDate)),
            (inflowCalc.cloneInflows, (startDate,)),
            (inflowCalc.autoAdjust, (startDate, useLimits_ON, freezeRain_ON)),
        ],
    }

    for location, calls in actions.items():
        for method, extra_args in calls:
            print("")
            print("Now running", method.__name__, "at", location)
            print("")
            try:
                method(officeID, location, *extra_args)
            except Exception as e:
                print("Error Completing action {0} at {1} {2}".format(method.__name__, officeID, location))
                print(e)
                print("")


if __name__ == "__main__":
    with regi_session():
        run_headless(run_calculations)
