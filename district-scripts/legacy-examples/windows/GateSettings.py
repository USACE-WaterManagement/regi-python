# the java Calendar class is used to create java Date objects
from java.util import Calendar
from java.util import TimeZone
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


# Time zone must be set because the Solaris time zone is UTC
timeZone = TimeZone.getTimeZone("US/Central")

# Defaults to start of the day 5 days ago, and ends at the top of the current hour today
# configure the start calendar
startCal = Calendar.getInstance(timeZone)
startCal.set(Calendar.HOUR_OF_DAY, 0)
startCal.set(Calendar.MINUTE, 0)
startCal.set(Calendar.SECOND, 0)
startCal.set(Calendar.MILLISECOND, 0)
startCal.add(Calendar.DATE, -5)

# configure the end calendar
endCal = Calendar.getInstance(timeZone)
endCal.set(Calendar.MINUTE, 0)
endCal.set(Calendar.SECOND, 0)
endCal.set(Calendar.MILLISECOND, 0)

# Calendar can be adjusted using the following functions:
#   startCal.set(Calendar.DATE, 1)          # Sets the date of the calendar.
#   startCal.set(Calendar.HOUR_OF_DAY, 1)   # Sets the hour of the day to 0100 (1-24)
#   startCal.set(Calendar.YEAR, 2020)       # Sets the year
#   startCal.set(Calendar.MONTH, 4)         # Sets the month (month 4 means May to Java)


# gateSettings contains four callable methods
#   void createGateSettings(String officeId, String locationStr, Date startDate, Date end) throws Exception;
#	void createGateSettingsGroup(String officeId, String locationStr, Date startDate, Date end, String groupId) throws Exception;
#	void createGateSettingsOutlet(String officeId, String locationStr, Date startDate, Date end, String outletId) throws Exception;
#	void createGateSettingsOutletFromTs(String officeId, String locationStr, Date startDate, Date end, String outletId, String tsId) throws Exception;

# This is an example of a call that would create gate settings at TainterGate 1 at WTYT2  from the specified input time series.
gateSettings.createGateSettingsOutletFromTs("SWF", "WTYT2",  startCal.getTime(), endCal.getTime(), "TG1", "WTYT2-TG1.Opening-Spillway_Gate.Const.0.0.MANUAL" )

# This is an example of a call that would create gate settings at TainterGate 1 at WTYT2 from the regi association configured input time series.
gateSettings.createGateSettingsOutlet("SWF", "WTYT2",  startCal.getTime(), endCal.getTime(), "TG1")

# This is an example of a call that would create gate settings at all outlets at WTYT2 which are in the TainterGateWTY group from the association configured time series.
gateSettings.createGateSettingsGroup("SWF", "WTYT2",  startCal.getTime(), endCal.getTime(), "WTYT2-TainterGateWTY" )

# This is an example of a call that would create gate settings for every outlet in a rating group at WTYT2.
gateSettings.createGateSettings("SWF", "WTYT2",  startCal.getTime(), endCal.getTime() )



