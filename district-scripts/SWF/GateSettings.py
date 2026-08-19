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

    # this gets a scriptable Gate Settings object
    gateSettings = registry.getCalculation(1.0, "Gate Settings")

    # Time zone must be set explicitly because the JVM's default timezone is
    # UTC, not the district's local time. (The previous Calendar.getInstance()
    # calls here had no explicit timezone and silently depended on whatever
    # timezone the host happened to be configured with.)
    central = ZoneInfo("America/Chicago")
    today_midnight = datetime.now(central).replace(hour=0, minute=0, second=0, microsecond=0)

    # start: 5 days ago, at midnight
    start_date = (today_midnight - timedelta(days=5)).astimezone(timezone.utc)
    # end: tomorrow, at midnight
    end_date = (today_midnight + timedelta(days=1)).astimezone(timezone.utc)

    # gateSettings contains four callable methods
    #   void createGateSettings(String officeId, String locationStr, Instant startDate, Instant end) throws Exception;
    #   void createGateSettingsGroup(String officeId, String locationStr, Instant startDate, Instant end, String groupId) throws Exception;
    #   void createGateSettingsOutlet(String officeId, String locationStr, Instant startDate, Instant end, String outletId) throws Exception;
    #   void createGateSettingsOutletFromTs(String officeId, String locationStr, Instant startDate, Instant end, String outletId, String tsId) throws Exception;

    gateSettings.createGateSettingsOutletFromTs("SWF", "FFLT2",  start_date, end_date, "Release", "FFLT2.Opening.Const.0.0.Rev-TRWD-Decodes" )
    gateSettings.createGateSettingsOutletFromTs("SWF", "EAMT2",  start_date, end_date, "Release", "EAMT2.Opening.Const.0.0.Rev-TRWD-Decodes" )
    gateSettings.createGateSettingsOutletFromTs("SWF", "TRNT2",  start_date, end_date, "Release", "TRNT2.Opening.Const.0.0.Rev-TRWD-Decodes" )
    gateSettings.createGateSettingsOutletFromTs("SWF", "BPRT2",  start_date, end_date, "Release", "BPRT2.Opening.Const.0.0.Rev-TRWD-Decodes" )
    gateSettings.createGateSettingsOutletFromTs("SWF", "LLST2",  start_date, end_date, "Release", "LLST2.Opening.Const.0.0.Rev-BRA-Decodes" )
    gateSettings.createGateSettingsOutletFromTs("SWF", "GBYT2",  start_date, end_date, "Release", "GBYT2.Opening.Const.0.0.Rev-BRA-Decodes" )
    gateSettings.createGateSettingsOutletFromTs("SWF", "PSMT2",  start_date, end_date, "Release", "PSMT2.Opening.Const.0.0.Rev-BRA-Decodes" )
    gateSettings.createGateSettingsOutletFromTs("SWF", "MSDT2",  start_date, end_date, "Release", "MSDT2.Opening.Const.0.0.Rev-LCRA-Decodes" )
    gateSettings.createGateSettingsOutletFromTs("SWF", "FRHT2",  start_date, end_date, "Release", "FRHT2.Opening.Const.0.0.Raw-Observer" )
    gateSettings.createGateSettingsOutletFromTs("SWF", "GPET2",  start_date, end_date, "Release", "GPET2.Opening.Const.0.0.Raw-Observer" )






if __name__ == "__main__":
    with regi_session():
        run_headless(run_calculations)
