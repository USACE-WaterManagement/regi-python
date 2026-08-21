from regi_python import regi_session, run_headless


def calculate_gate_settings(registry):
    # Java imports must happen after regi_session starts the JVM.
    from java.util import Calendar, TimeZone

    # this gets a scriptable Gate Settings object
    gate_settings = registry.getCalculation(1.0, "Gate Settings")

    # Time zone must be set because the Solaris time zone is UTC
    time_zone = TimeZone.getTimeZone("US/Central")
    # configure the start calendar
    start_cal = Calendar.getInstance(time_zone)
    start_cal.clear()
    start_cal.set(Calendar.YEAR, 2015)
    start_cal.set(Calendar.MONTH, 4)

    # configure the end calendar
    end_cal = Calendar.getInstance(time_zone)
    end_cal.clear()
    end_cal.set(Calendar.YEAR, 2015)
    end_cal.set(Calendar.MONTH, 6)

    # gate_settings contains four callable methods
    #   void createGateSettings(String officeId, String locationStr, Date startDate, Date end) throws Exception;
    #   void createGateSettingsGroup(String officeId, String locationStr, Date startDate, Date end, String groupId) throws Exception;
    #   void createGateSettingsOutlet(String officeId, String locationStr, Date startDate, Date end, String outletId) throws Exception;
    #   void createGateSettingsOutletFromTs(String officeId, String locationStr, Date startDate, Date end, String outletId, String tsId) throws Exception;

    # This is an example of a call that would create gate settings at TainterGate 1 at WTYT2 from the specified input time series.
    gate_settings.createGateSettingsOutletFromTs("SWF", "WTYT2", start_cal.getTime(), end_cal.getTime(), "TG1", "WTYT2-TG1.Opening-Spillway_Gate.Const.0.0.MANUAL")

    # This is an example of a call that would create gate settings at TainterGate 1 at WTYT2 from the regi association configured input time series.
    gate_settings.createGateSettingsOutlet("SWF", "WTYT2", start_cal.getTime(), end_cal.getTime(), "TG1")

    # This is an example of a call that would create gate settings at all outlets at WTYT2 which are in the TainterGateWTY group from the association configured time series.
    gate_settings.createGateSettingsGroup("SWF", "WTYT2", start_cal.getTime(), end_cal.getTime(), "WTYT2-TainterGateWTY")

    # This is an example of a call that would create gate settings for every outlet in a rating group at WTYT2.
    gate_settings.createGateSettings("SWF", "WTYT2", start_cal.getTime(), end_cal.getTime())


if __name__ == "__main__":
    with regi_session():
        run_headless(calculate_gate_settings)
