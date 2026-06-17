# the java Calendar class is used to create java Date objects
from java.util import Calendar
from java.util import TimeZone
from usace.rowcps.headless.calculator.inflow import InflowComputationStorageOption

# this gets a ScriptableInflow instance.
inflowCalc = registry.getCalculation(1.0, "Inflow")

# configure the start calendar
##startCal = Calendar.getInstance(TimeZone.getTimeZone('US/Central'))
##
##
##startCal.clear()
##startCal.set(Calendar.YEAR, 2019)
##startCal.set(Calendar.MONTH, 1)
##
##endCal = Calendar.getInstance(TimeZone.getTimeZone('US/Central'))
##endCal.clear()
##endCal.set(Calendar.YEAR, 2019)
##endCal.set(Calendar.MONTH, 1)
##endCal.set(Calendar.DAY_OF_MONTH, 4)

startCal = Calendar.getInstance(TimeZone.getTimeZone('US/Central'))
startCal.add(Calendar.DAY_OF_MONTH, -4)
startCal.set(Calendar.HOUR, 0)        ######use Calendar.HOUR_OF_DAY
startCal.set(Calendar.MINUTE, 0)
startCal.set(Calendar.SECOND, 0)
startCal.set(Calendar.MILLISECOND, 0)
# create a java Calendar object that will be used to create the end Date
endCal = Calendar.getInstance(TimeZone.getTimeZone('US/Central'))
endCal.add(Calendar.DAY_OF_MONTH, 1)
endCal.set(Calendar.HOUR, 0)
endCal.set(Calendar.MINUTE, 0)
endCal.set(Calendar.SECOND, 0)
endCal.set(Calendar.MILLISECOND, 0)

# inflowCalc includes a setComputationStorageOptions function, which takes in either one or many
# InflowComputationStorageOption values.  This is used by computeInflow to determine if it should save additional
# computed values like evaporation as flow and project releases.
# 
# The InflowComputationStorageOption enum contains two values:
# 	EVAP_AS_FLOW
# 	PROJECT_RELEASES
#
# None is supported by setComputationStorageOptions as well, and clears out all storage options.
# 
# inflowCalc.setComputationStorageOptions is entirely optional, and if it's not used no additional computed values will
# be stored with the computed inflow
# 
# Example uses:
#inflowCalc.setComputationStorageOptions(None)
#inflowCalc.setComputationStorageOptions(InflowComputationStorageOption.EVAP_AS_FLOW)
#inflowCalc.setComputationStorageOptions(InflowComputationStorageOption.PROJECT_RELEASES)

#inflowCalc.setComputationStorageOptions(InflowComputationStorageOption.EVAP_AS_FLOW, InflowComputationStorageOption.PROJECT_RELEASES)


locationList = ["WTYT2","JSPT2","TBLT2","SCLT2","TXKT2","BSLT2","JFNT2","CLDL1",
                "BPRT2","EAMT2","FLWT2","BNBT2","JPLT2","GPET2","RRLT2","LEWT2",
                "GPVT2","LVNT2","FRHT2","TRNT2","DAWT2","BDWT2","FFLT2","PSMT2",
                "GBYT2","ALAT2","ACTT2","PCTT2","BLNT2","STIT2","GGLT2","GNGT2",
                "SOMT2","LLST2","TBRT2","SAGT2","HORT2","SMCT2","MSDT2"]
for loc in locationList:
    inflowCalc.computeInflow("SWF", loc, startCal.getTime(), endCal.getTime())
