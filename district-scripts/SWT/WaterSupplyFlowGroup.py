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

#LoggingOptions.setMetricsEnabled(True)

# not all of Regi is scriptable, registry is an object created by the java class RegiCLI that contains a list of
# the implemented scriptable calculations
names = registry.getNames(1.0)

# this retrieves a Gate Flow calculation object
gateCalc = registry.getCalculation(1.0, "Gate Flow")

# the gate flow calculations requires a start and end time.
# here we create a java Calendar object that will be used to create the start Date
#
# use the current date minus 5 days.
#
startCal = Calendar.getInstance()
#startCal.clear()
#startCal.set(Calendar.YEAR, 2016)
#startCal.set(Calendar.MONTH, 8)
startCal.add(Calendar.DAY_OF_MONTH, -5)
#startCal.set(Calendar.HOUR, 0) 
#startCal.add(Calendar.HOUR, -4) 
startCal.set(Calendar.MINUTE, 0)
startCal.set(Calendar.SECOND, 0)
startCal.set(Calendar.MILLISECOND, 0)

print "this is the place to write the startCal!"
print startCal.getTime().toString()

# create a java Calendar object that will be used to create the end Date
# use the current date.
#
endCal = Calendar.getInstance()
#remove the next line when the headless time options are fixed
#endCal.add(Calendar.DAY_OF_MONTH, 1)  
#endCal.set(Calendar.HOUR, 16) 
#endCal.set(Calendar.YEAR, 2018)
#endCal.set(Calendar.MONTH, 6)
#endCal.set(Calendar.DAY_OF_MONTH, 6)
endCal.set(Calendar.MINUTE, 0)
endCal.set(Calendar.SECOND, 0)
endCal.set(Calendar.MILLISECOND, 0)

print "this is the place to write the endCal!"
print endCal.getTime().toString()

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
gateCalc.computeFlowGroup("SWT", "ARBU",  startCal.getTime(), endCal.getTime(), "Flow.ARBU.Pump_Out_Total")

#ARCA
gateCalc.computeFlowGroup("SWT", "ARCA",  startCal.getTime(), endCal.getTime(), "Flow.ARCA.Pump_Out_Total")

#CHEN
gateCalc.computeFlowGroup("SWT", "CHEN",  startCal.getTime(), endCal.getTime(), "Flow.CHEN.Pump_Out_Total")

#ELDR
gateCalc.computeFlowGroup("SWT", "ELDR",  startCal.getTime(), endCal.getTime(), "Flow.ELDR.Pump_Out_Total")

#FCOB
gateCalc.computeFlowGroup("SWT", "FCOB",  startCal.getTime(), endCal.getTime(), "Flow.FCOB.Pump_Out_Total")

#FOSS
gateCalc.computeFlowGroup("SWT", "FOSS",  startCal.getTime(), endCal.getTime(), "Flow.FOSS.Pump_Out_Total")

#MCGE
gateCalc.computeFlowGroup("SWT", "MCGE",  startCal.getTime(), endCal.getTime(), "Flow.MCGE.Pump_Out_Total")

#MERE
gateCalc.computeFlowGroup("SWT", "MERE",  startCal.getTime(), endCal.getTime(), "Flow.MERE.Pump_Out_Total")

#OOLO
gateCalc.computeFlowGroup("SWT", "OOLO",  startCal.getTime(), endCal.getTime(), "Flow.OOLO.Pump_Out_Total")

#PATM
gateCalc.computeFlowGroup("SWT", "PATM",  startCal.getTime(), endCal.getTime(), "Flow.PATM.Pump_Out_Total")

#THUN
gateCalc.computeFlowGroup("SWT", "THUN",  startCal.getTime(), endCal.getTime(), "Flow.THUN.Pump_Out_Total")

#TOMS
gateCalc.computeFlowGroup("SWT", "TOMS",  startCal.getTime(), endCal.getTime(), "Flow.TOMS.Pump_Out_Total")

#WAUR
gateCalc.computeFlowGroup("SWT", "WAUR",  startCal.getTime(), endCal.getTime(), "Flow.WAUR.Pump_Out_Total")

