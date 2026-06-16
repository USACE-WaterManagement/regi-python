from java.util import Calendar
from java.util import TimeZone

# this retrieves a Sig States caluclation object
sigstates = registry.getCalculation(1.0, "Import Sig States")

#sigstates has the following API exposed:
#
#    public void importSigStages(String file, Date effectiveDate);

# Purpose:
# Sigstages_DBImport.py imports each of the location levels from
# the sig stage data into the REGI database for use in the REGI application

# the file to be read in order to import the correct data to the REGI sigstates
# if you have your own .csv file, you can enter its full name here to import 
# from that location instead, but sigstages.csv is the default generated from
# the Sigstages_Download script
inpath = "sigstages.csv"

# Time zone must be set because the Solaris time zone is UTC
timeZone = TimeZone.getTimeZone("US/Central")
# the sig states calculation requires an effective date
# here we create a java Calendar object that will be used to create that date
cal = Calendar.getInstance(timeZone)
cal.clear()
cal.set(Calendar.YEAR, 1899)
cal.set(Calendar.MONTH, Calendar.JANUARY)
cal.set(Calendar.DAY_OF_MONTH, 1)

# the importSigStates method takes:
# inpath (csv file)
# effective date (calendar date)
sigstates.importSigStages(inpath, cal.getTime())
