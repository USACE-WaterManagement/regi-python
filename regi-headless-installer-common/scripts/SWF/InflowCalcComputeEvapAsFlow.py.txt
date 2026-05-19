# the java Calendar class is used to create java Date objects
from java.util import Calendar
from java.util import TimeZone


# this gets a ScriptableInflow instance.
inflowCalc = registry.getCalculation(1.0, "Inflow")

# configure the start calendar
##startCal = Calendar.getInstance(TimeZone.getTimeZone('US/Central'))
##
##
##startCal.clear()
##startCal.set(Calendar.YEAR, 2018)
##startCal.set(Calendar.MONTH, 11)
##
##endCal = Calendar.getInstance(TimeZone.getTimeZone('US/Central'))
##endCal.clear()
##endCal.set(Calendar.YEAR, 2019)
##endCal.set(Calendar.MONTH, 0)
##endCal.set(Calendar.DAY_OF_MONTH, 7)

startCal = Calendar.getInstance(TimeZone.getTimeZone('US/Central'))
# startCal.clear()
startCal.add(Calendar.DAY_OF_MONTH, -5)
startCal.set(Calendar.HOUR_OF_DAY, 0)
startCal.set(Calendar.MINUTE, 0)
startCal.set(Calendar.SECOND, 0)
startCal.set(Calendar.MILLISECOND, 0)
# startCal.set(Calendar.YEAR, 2015)
# startCal.set(Calendar.MONTH, 9)

# create a java Calendar object that will be used to create the end Date
endCal = Calendar.getInstance(TimeZone.getTimeZone('US/Central'))
# endCal.clear()
endCal.add(Calendar.DAY_OF_MONTH, 1)
endCal.set(Calendar.HOUR_OF_DAY, 0)
endCal.set(Calendar.MINUTE, 0)
endCal.set(Calendar.SECOND, 0)
endCal.set(Calendar.MILLISECOND, 0)

locationList = ["WTYT2","JSPT2","TBLT2","SCLT2","TXKT2","BSLT2","JFNT2","CLDL1",
                "BPRT2","EAMT2","FLWT2","BNBT2","JPLT2","GPET2","RRLT2","LEWT2",
                "GPVT2","LVNT2","FRHT2","TRNT2","DAWT2","BDWT2","FFLT2","PSMT2",
                "GBYT2","ALAT2","ACTT2","PCTT2","BLNT2","STIT2","GGLT2","GNGT2",
                "SOMT2","LLST2","TBRT2","SAGT2","HORT2","MSDT2","SMCT2"]

for loc in locationList:
    inflowCalc.computeEvapAsFlow("SWF", loc,  startCal.getTime(), endCal.getTime())
