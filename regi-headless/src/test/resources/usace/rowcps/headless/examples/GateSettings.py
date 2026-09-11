from regi_python import regi_session, run_headless


def calculate_gate_settings(registry):
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo


    # this gets a scriptable Gate Settings object
    gate_settings = registry.getCalculation(1.0, "Gate Settings")

    # Time zone must be set explicitly because the JVM's default timezone is
    # UTC, not the district's local time.
    central = ZoneInfo("America/Chicago")
    # Java's Calendar.MONTH was 0-indexed (4 == May, 6 == July); datetime.month
    # is 1-indexed, so we use 5 and 7 here for the same dates.
    start_date = (datetime(2015, 5, 1, tzinfo=central)).astimezone(timezone.utc)
    end_date = (datetime(2015, 7, 1, tzinfo=central)).astimezone(timezone.utc)

    # gate_settings contains four callable methods
    #   void createGateSettings(String officeId, String locationStr, Instant startDate, Instant end) throws Exception;
    #   void createGateSettingsGroup(String officeId, String locationStr, Instant startDate, Instant end, String groupId) throws Exception;
    #   void createGateSettingsOutlet(String officeId, String locationStr, Instant startDate, Instant end, String outletId) throws Exception;
    #   void createGateSettingsOutletFromTs(String officeId, String locationStr, Instant startDate, Instant end, String outletId, String tsId) throws Exception;

    # This is an example of a call that would create gate settings at TainterGate 1 at WTYT2 from the specified input time series.
    gate_settings.createGateSettingsOutletFromTs("SWF", "WTYT2", start_date, end_date, "TG1", "WTYT2-TG1.Opening-Spillway_Gate.Const.0.0.MANUAL")

    # This is an example of a call that would create gate settings at TainterGate 1 at WTYT2 from the regi association configured input time series.
    gate_settings.createGateSettingsOutlet("SWF", "WTYT2", start_date, end_date, "TG1")

    # This is an example of a call that would create gate settings at all outlets at WTYT2 which are in the TainterGateWTY group from the association configured time series.
    gate_settings.createGateSettingsGroup("SWF", "WTYT2", start_date, end_date, "WTYT2-TainterGateWTY")

    # This is an example of a call that would create gate settings for every outlet in a rating group at WTYT2.
    gate_settings.createGateSettings("SWF", "WTYT2", start_date, end_date)


if __name__ == "__main__":
    with regi_session():
        run_headless(calculate_gate_settings)
