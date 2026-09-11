from regi_python import regi_session, run_headless


def run_calculations(registry):
    from datetime import datetime, timedelta, timezone
    from zoneinfo import ZoneInfo

    # Java imports must happen after regi_session starts the JVM.
    from usace.rowcps.headless import LoggingOptions


    def compute_All_Flowgroups(officeID, location, start_date, end_date):
        # Takes in locations defined by user in group and computes all flow groups
        try:
            gateCalc.computeAll(officeID, location, start_date, end_date)
        except Exception as e:
            print("Error Computing all Flow Groups at {0} {1}".format(officeID, location))
            print(e)
            print('')


    def compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroup):
        try:
            gateCalc.computeFlowGroup(officeID, location, start_date, end_date, "Flow.{0}.{1}".format(location, flowGroup))
        except Exception as e:
            print("Error Computing Flow Group {0} at {1}".format(officeID, location))
            print(e)
            print('')

        # #gateCalc.computeFlowGroup("SWF", "ACTT2",  start_date, end_date, "Flow.ACTT2.Pump_Out_Total")
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

    # not all of Regi is scriptable, registry is an object created by the java class RegiCLI that contains a list of
    # the implemented scriptable calculations
    names = registry.getNames(1.0)

    # this retrieves a Gate Flow calculation object
    gateCalc = registry.getCalculation(1.0, "Gate Flow")

    # Time zone must be set explicitly because the JVM's default timezone is
    # UTC, not the district's local time.
    central = ZoneInfo("America/Chicago")

    # Defaults to start of the day 5 days ago, and ends at the top of the current hour today
    end_date_dt = datetime.now(central).replace(minute=0, second=0, microsecond=0)
    start_date_dt = end_date_dt - timedelta(days=5)
    #start_date_dt = end_date_dt - timedelta(days=5, hours=7)
    #remove or comment out the next line when done!! it was for a big backload  ajm
    #start_date_dt = start_date_dt - timedelta(days=305)  # ~10 months

    start_date = start_date_dt.astimezone(timezone.utc)
    end_date = end_date_dt.astimezone(timezone.utc)

    # Dates can be adjusted using normal datetime arithmetic/replace, e.g.:
    #   start_date_dt = start_date_dt.replace(day=1)                  # start of month
    #   start_date_dt = start_date_dt.replace(hour=1)                 # 0100 local time
    #   start_date_dt = start_date_dt.replace(year=2020, month=5)     # month is 1-indexed here

    officeID = "SWT"

    # the gateCalc object can perform its calculation for a single flow group
    # the computeFlowGroup method takes:
    # officeId
    # projectId
    # startDate
    # endDate
    # gateCalc.computeFlowGroup("SWF", "LEWT2",  start_date, end_date, "Flow.LEWT2.ConduitGate_Total")


    #
    #  GROUP 7 PROJECTS (SELF-TIMED TRANSMISSIONS WITHIN 33 TO 36 MINUTES PAST THE TOP OF THE HOUR)
    #

    #CHOU
    gateCalc.computeFlowGroup("SWT", "CHOU",  start_date, end_date, "Flow.CHOU.Project_Total")
    gateCalc.computeFlowGroup("SWT", "CHOU",  start_date, end_date, "Flow.CHOU.Gated_Total")

    #NEWT
    gateCalc.computeFlowGroup("SWT", "NEWT",  start_date, end_date, "Flow.NEWT.Project_Total")
    gateCalc.computeFlowGroup("SWT", "NEWT",  start_date, end_date, "Flow.NEWT.Gated_Total")

    #TOMS
    gateCalc.computeFlowGroup("SWT", "TOMS",  start_date, end_date, "Flow.TOMS.Project_Total")
    gateCalc.computeFlowGroup("SWT", "TOMS",  start_date, end_date, "Flow.TOMS.Gated_Total")

    #TORO
    gateCalc.computeFlowGroup("SWT", "TORO",  start_date, end_date, "Flow.TORO.Project_Total")
    gateCalc.computeFlowGroup("SWT", "TORO",  start_date, end_date, "Flow.TORO.Gated_Total")

    #ALTU
    gateCalc.computeFlowGroup("SWT", "ALTU",  start_date, end_date, "Flow.ALTU.Project_Total")
    gateCalc.computeFlowGroup("SWT", "ALTU",  start_date, end_date, "Flow.ALTU.Gated_Total")

    #ELDR
    gateCalc.computeFlowGroup("SWT", "ELDR",  start_date, end_date, "Flow.ELDR.Project_Total")
    gateCalc.computeFlowGroup("SWT", "ELDR",  start_date, end_date, "Flow.ELDR.Gated_Total")

    #CHEN
    gateCalc.computeFlowGroup("SWT", "CHEN",  start_date, end_date, "Flow.CHEN.Project_Total")
    gateCalc.computeFlowGroup("SWT", "CHEN",  start_date, end_date, "Flow.CHEN.Gated_Total")

    #JOHN
    gateCalc.computeFlowGroup("SWT", "JOHN",  start_date, end_date, "Flow.JOHN.Project_Total")
    gateCalc.computeFlowGroup("SWT", "JOHN",  start_date, end_date, "Flow.JOHN.Gated_Total")






if __name__ == "__main__":
    with regi_session():
        run_headless(run_calculations)
