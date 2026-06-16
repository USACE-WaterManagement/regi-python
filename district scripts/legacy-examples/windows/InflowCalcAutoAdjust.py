# the java Calendar class is used to create java Date objects
from java.util import Calendar
from java.util import TimeZone
from usace.rowcps.headless import LoggingOptions


def auto_Adjust(officeID, location, startCal, useLimits, freezeRain):
    # Takes in locations defined by user in group and adjusts the selected inflow. If a location fails or has an error, the script will continue. check the console log
    # for any further information.
    try:
        inflowCalc.autoAdjust(officeID, location, startCal.getTime(), useLimits, freezeRain)
    except Exception as e:
        print "Error Adjusting Values at {0} {1}".format(officeID, location)
        print e
        print ""

# Description of: LoggingOptions.setDbMessageLevel(int level)
#
# Adds Time Series logging messages in the OracleTimeSeriesDaoImpl.  Recommended
# level is 2, as this provides basic information about the time series
# retrieval/storage.
#
# Message Level | Description
# --------------|-------------------------------------------------------------------------------------------------------------------------------|
# <=0           | Default value, does not do anything.  Lower values do not change behavior.                                                    |
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

# Defaults to day one of the current month at 0000
# configure the start calendar
startCal = Calendar.getInstance(TimeZone.getTimeZone('US/Central'))
startCal.set(Calendar.DATE, 1)
startCal.set(Calendar.HOUR_OF_DAY, 0)
startCal.set(Calendar.MINUTE, 0)
startCal.set(Calendar.SECOND, 0)
startCal.set(Calendar.MILLISECOND, 0)

# Calendar can be adjusted using the following functions:
#   startCal.set(Calendar.DATE, 1)          # Sets the date of the calendar.
#   startCal.set(Calendar.HOUR_OF_DAY, 1)   # Sets the hour of the day to 0100 (1-24)
#   startCal.set(Calendar.YEAR, 2020)       # Sets the year
#   startCal.set(Calendar.MONTH, 4)         # Sets the month (month 4 means May to Java)


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
# 	useLimits
# 	freezeRain

# This autoAdjusts for ACTT2 and ALAT2. Several locations are commented out and can be commented back in any order. Additional stations can be added
# to the end provided they follow the same format. UseLimits and FreezeRain are also controllable arguments for AutoAdjust. By setting "useLimits_ON" to True,
# the function will use the "useLimits command. By setting it to "False", it will be turned off. This functions the same way for "freezeRain_ON"

officeID = "SWF"
useLimits_ON = False
freezeRain_ON = False
locationList = ["ACTT2",
                "ALAT2",
#                 "BLNT2",
#                 "BNBT2",
#                 "CLDL1",
#                 "DAWT2",
                "ACTT2",
                "TXKT2",
                ]
for location in locationList:
    print "Now Running", location
    auto_Adjust(officeID, location, startCal, useLimits_ON, freezeRain_ON)



