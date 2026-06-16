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

# this gets a scriptable Pool Percent object
percentCalc = registry.getCalculation(1.0, "Pool Percent")

# Time zone must be set because the Solaris time zone is UTC
timeZone = TimeZone.getTimeZone("US/Central")
# configure the start calendar
startCal = Calendar.getInstance(timeZone)
startCal.clear()
startCal.set(Calendar.YEAR, 2015)
startCal.set(Calendar.MONTH, 4)

# configure the end calendar
endCal = Calendar.getInstance(timeZone)
endCal.clear()
endCal.set(Calendar.YEAR, 2015)
endCal.set(Calendar.MONTH, 6)


# percentCalc contains a single callable method calculatePoolPercents which takes the followind arguments:
# officeId
# locationId
# startDate
# endDate
# This recomputes the pool percentages for SWF.LEWT2
percentCalc.calculatePoolPercents("SWF", "LEWT2",  startCal.getTime(), endCal.getTime())


