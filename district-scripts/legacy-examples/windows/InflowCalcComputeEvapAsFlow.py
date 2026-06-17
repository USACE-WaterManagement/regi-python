# the java Calendar class is used to create java Date objects
from java.util import Calendar
from java.util import TimeZone

# this gets a ScriptableInflow instance.
inflowCalc = registry.getCalculation(1.0, "Inflow")

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

# This computes and saves evap as flow for EUFA in May 2018
inflowCalc.computeEvapAsFlow("SWT", "EUFA",  startCal.getTime(), endCal.getTime())
