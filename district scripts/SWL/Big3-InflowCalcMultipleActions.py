# the java Calendar class is used to create java Date objects
from java.util import Calendar
from java.util import TimeZone
from usace.rowcps.headless import LoggingOptions

def inflow_Actions(function, officeID, location, startCal, endCal, uselimits, freezerain):
    # Takes in locations defined by user in group and computes the given command at the given station.
    try:
        if function.lower() == "cloneinflows":
            inflowCalc.cloneInflows(officeID, location,  startCal.getTime())
	elif function.lower() == "computeinflow":
	    inflowCalc.computeInflow(officeID, location, startCal.getTime(), endCal.getTime())
        elif function.lower() == "zeronegatives":
            inflowCalc.zeroNegatives(officeID, location,  startCal.getTime())
        elif function.lower() == "balanceall":
            inflowCalc.balanceAll(officeID, location,  startCal.getTime())
        elif function.lower() == "autoadjust":
            inflowCalc.autoAdjust(officeID, location,  startCal.getTime(), uselimits, freezerain)
        else:
            print "Input command", function, "is not recognized. Please edit your input and try again."
    except Exception as e:
        print "Error Completing action {0} at {1} {2}".format(function, officeID, location)
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

# configure the start calendar'
#startCal = Calendar.getInstance(TimeZone.getTimeZone('US/Central'))
timeZone = TimeZone.getTimeZone("US/Central")

#startCal.clear()
#startCal.set(Calendar.YEAR, 2015)
#startCal.set(Calendar.MONTH, 4)

startCal = Calendar.getInstance(timeZone)
startCal.add(Calendar.DAY_OF_MONTH, -7)
startCal.set(Calendar.HOUR_OF_DAY, 0)
startCal.set(Calendar.MINUTE, 0)
startCal.set(Calendar.SECOND, 0)
startCal.set(Calendar.MILLISECOND, 0)

endCal = Calendar.getInstance(timeZone)
endCal.add(Calendar.DAY_OF_MONTH, 1)
endCal.set(Calendar.HOUR_OF_DAY, 0)
endCal.set(Calendar.MINUTE, 0)
endCal.set(Calendar.SECOND, 0)
endCal.set(Calendar.MILLISECOND, 0)

officeID = "SWL"

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
useLimits_ON = False
freezeRain_ON = False

# Commands can be input in a list format as seen below. The format is as follows "[ACTION] @ [LOCATION]", reading like "Perform [ACITON] at [LOCATION]. 
# The action must come first, and they must be separated by a "@" symbol.
# Spaces between the Action/Location and "@" symbol can vary, although 1 space is recommended for readability. Lines can be commented out as needed.
actions = ["computeInflow @ Blue_Mtn_Dam",
           "cloneInflows @ Blue_Mtn_Dam",
           "autoAdjust @ Blue_Mtn_Dam",
	   "computeInflow @ Nimrod_Dam",
	   "cloneInflows @ Nimrod_Dam",
	   "autoAdjust @ Nimrod_Dam",
	   "computeInflow @ Clearwater_Dam",
	   "cloneInflows @ Clearwater_Dam",
	   "autoAdjust @ Clearwater_Dam",
           ]

for command in actions:
    location = command.split('@')[1].strip()
    function = command.split('@')[0].strip()
    print ""
    print "Now running", function, "at", location
    print ""
    inflow_Actions(function, officeID, location, startCal, endCal, useLimits_ON, freezeRain_ON)
