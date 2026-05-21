# the java Calendar class is used to create java Date objects
from java.util import Calendar
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

# configure the start calendar
startCal = Calendar.getInstance()
#startCal.clear()
startCal.add(Calendar.DAY_OF_MONTH, -5)
startCal.set(Calendar.HOUR, 0)        ######use Calendar.HOUR_OF_DAY
startCal.set(Calendar.MINUTE, 0)
startCal.set(Calendar.SECOND, 0)
startCal.set(Calendar.MILLISECOND, 0)
# create a java Calendar object that will be used to create the end Date
endCal = Calendar.getInstance()
endCal.add(Calendar.DAY_OF_MONTH, 1)
endCal.set(Calendar.HOUR, 0)
endCal.set(Calendar.MINUTE, 0)
endCal.set(Calendar.SECOND, 0)
endCal.set(Calendar.MILLISECOND, 0)
#endCal.clear()
#endCal.set(Calendar.YEAR, 2016)
#endCal.set(Calendar.MONTH, 4)


# gateSettings contains four callable methods
#   void createGateSettings(String officeId, String locationStr, Date startDate, Date end) throws Exception;
#	void createGateSettingsGroup(String officeId, String locationStr, Date startDate, Date end, String groupId) throws Exception;
#	void createGateSettingsOutlet(String officeId, String locationStr, Date startDate, Date end, String outletId) throws Exception;
#	void createGateSettingsOutletFromTs(String officeId, String locationStr, Date startDate, Date end, String outletId, String tsId) throws Exception;

gateSettings.createGateSettingsOutletFromTs("SWF", "FFLT2",  startCal.getTime(), endCal.getTime(), "Release", "FFLT2.Opening.Const.0.0.Rev-TRWD-Decodes" )
gateSettings.createGateSettingsOutletFromTs("SWF", "EAMT2",  startCal.getTime(), endCal.getTime(), "Release", "EAMT2.Opening.Const.0.0.Rev-TRWD-Decodes" )
gateSettings.createGateSettingsOutletFromTs("SWF", "TRNT2",  startCal.getTime(), endCal.getTime(), "Release", "TRNT2.Opening.Const.0.0.Rev-TRWD-Decodes" )
gateSettings.createGateSettingsOutletFromTs("SWF", "BPRT2",  startCal.getTime(), endCal.getTime(), "Release", "BPRT2.Opening.Const.0.0.Rev-TRWD-Decodes" )
gateSettings.createGateSettingsOutletFromTs("SWF", "LLST2",  startCal.getTime(), endCal.getTime(), "Release", "LLST2.Opening.Const.0.0.Rev-BRA-Decodes" )
gateSettings.createGateSettingsOutletFromTs("SWF", "GBYT2",  startCal.getTime(), endCal.getTime(), "Release", "GBYT2.Opening.Const.0.0.Rev-BRA-Decodes" )
gateSettings.createGateSettingsOutletFromTs("SWF", "PSMT2",  startCal.getTime(), endCal.getTime(), "Release", "PSMT2.Opening.Const.0.0.Rev-BRA-Decodes" )
gateSettings.createGateSettingsOutletFromTs("SWF", "MSDT2",  startCal.getTime(), endCal.getTime(), "Release", "MSDT2.Opening.Const.0.0.Rev-LCRA-Decodes" )
gateSettings.createGateSettingsOutletFromTs("SWF", "FRHT2",  startCal.getTime(), endCal.getTime(), "Release", "FRHT2.Opening.Const.0.0.Raw-Observer" )
gateSettings.createGateSettingsOutletFromTs("SWF", "GPET2",  startCal.getTime(), endCal.getTime(), "Release", "GPET2.Opening.Const.0.0.Raw-Observer" )




