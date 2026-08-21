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

    #LoggingOptions.setMetricsEnabled(True)

    # not all of Regi is scriptable, registry is an object created by the java class RegiCLI that contains a list of
    # the implemented scriptable calculations
    names = registry.getNames(1.0)

    # this retrieves a Gate Flow calculation object
    gateCalc = registry.getCalculation(1.0, "Gate Flow")

    # Time zone must be set explicitly because the JVM's default timezone is
    # UTC, not the district's local time. (The previous Calendar.getInstance()
    # calls here had no explicit timezone and silently depended on whatever
    # timezone the host happened to be configured with.)
    #
    # use the current date minus 5 days.
    #
    central = ZoneInfo("America/Chicago")
    end_date_dt = datetime.now(central).replace(minute=0, second=0, microsecond=0)
    #end_date_dt = end_date_dt.replace(year=2016, month=9)  # month is 1-indexed here
    start_date_dt = end_date_dt - timedelta(days=5)
    #start_date_dt = start_date_dt.replace(hour=0)
    #start_date_dt = start_date_dt - timedelta(hours=4)

    start_date = start_date_dt.astimezone(timezone.utc)

    print("this is the place to write the start_date!")
    print(start_date.isoformat())

    # use the current date.
    #
    #remove the next line when the headless time options are fixed
    #end_date_dt = end_date_dt + timedelta(days=1)
    #end_date_dt = end_date_dt.replace(hour=16, year=2018, month=7, day=6)

    end_date = end_date_dt.astimezone(timezone.utc)

    print("this is the place to write the end_date!")
    print(end_date.isoformat())

    # the gateCalc object can perform its calculation for a single flow group
    # the computeFlowGroup method takes:
    # officeId
    # projectId
    # startDate
    # endDate


    #
    #  PROJECTS WITH WATER SUPPLY WITHDRAWS/RELEASES
    #


    #ARBU
    gateCalc.computeFlowGroup("SWT", "ARBU",  start_date, end_date, "Flow.ARBU.Pump_Out_Total")

    #ARCA
    gateCalc.computeFlowGroup("SWT", "ARCA",  start_date, end_date, "Flow.ARCA.Pump_Out_Total")

    #CHEN
    gateCalc.computeFlowGroup("SWT", "CHEN",  start_date, end_date, "Flow.CHEN.Pump_Out_Total")

    #ELDR
    gateCalc.computeFlowGroup("SWT", "ELDR",  start_date, end_date, "Flow.ELDR.Pump_Out_Total")

    #FCOB
    gateCalc.computeFlowGroup("SWT", "FCOB",  start_date, end_date, "Flow.FCOB.Pump_Out_Total")

    #FOSS
    gateCalc.computeFlowGroup("SWT", "FOSS",  start_date, end_date, "Flow.FOSS.Pump_Out_Total")

    #MCGE
    gateCalc.computeFlowGroup("SWT", "MCGE",  start_date, end_date, "Flow.MCGE.Pump_Out_Total")

    #MERE
    gateCalc.computeFlowGroup("SWT", "MERE",  start_date, end_date, "Flow.MERE.Pump_Out_Total")

    #OOLO
    gateCalc.computeFlowGroup("SWT", "OOLO",  start_date, end_date, "Flow.OOLO.Pump_Out_Total")

    #PATM
    gateCalc.computeFlowGroup("SWT", "PATM",  start_date, end_date, "Flow.PATM.Pump_Out_Total")

    #THUN
    gateCalc.computeFlowGroup("SWT", "THUN",  start_date, end_date, "Flow.THUN.Pump_Out_Total")

    #TOMS
    gateCalc.computeFlowGroup("SWT", "TOMS",  start_date, end_date, "Flow.TOMS.Pump_Out_Total")

    #WAUR
    gateCalc.computeFlowGroup("SWT", "WAUR",  start_date, end_date, "Flow.WAUR.Pump_Out_Total")



if __name__ == "__main__":
    with regi_session():
        run_headless(run_calculations)
