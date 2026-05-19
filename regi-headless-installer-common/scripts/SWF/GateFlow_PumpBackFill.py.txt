from java.util import Calendar
from usace.rowcps.headless import LoggingOptions

def compute_All_Flowgroups(officeID, location, startCal, endCal):
    # Takes in locations defined by user in group and computes all flow groups
    try:
        gateCalc.computeAll(officeID, location, startCal.getTime(), endCal.getTime())
    except Exception as e:
        print "Error Computing all Flow Groups at {0} {1}".format(officeID, location)
        print e
        print ''


def compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroup):
    try:
        gateCalc.computeFlowGroup(officeID, location, startCal.getTime(), endCal.getTime(), "Flow.{0}.{1}".format(location, flowGroup))
    except Exception as e:
        print "Error Computing Flow Group {0} at {1}".format(officeID, location)
        print e
        print ''

    # #gateCalc.computeFlowGroup("SWF", "ACTT2",  startCal.getTime(), endCal.getTime(), "Flow.ACTT2.Pump_Out_Total")
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

# not all of Regi is scriptable, registry is an object created by the java class RegiCLI that contains a list of
# the implemented scriptable calculations
names = registry.getNames(1.0)

# this retrieves a Gate Flow calculation object
gateCalc = registry.getCalculation(1.0, "Gate Flow")

# the gate flow calculations requires a start and end time.
# here we create a java Calendar object that will be used to create the start Date
startCal = Calendar.getInstance()
# startCal.clear()
startCal.add(Calendar.DAY_OF_MONTH, -1)
startCal.set(Calendar.HOUR, 0)
startCal.set(Calendar.MINUTE, 0)
startCal.set(Calendar.SECOND, 0)
startCal.set(Calendar.MILLISECOND, 0)
# startCal.set(Calendar.YEAR, 2015)
# startCal.set(Calendar.MONTH, 9)

# create a java Calendar object that will be used to create the end Date
endCal = Calendar.getInstance()
# endCal.clear()
endCal.add(Calendar.DAY_OF_MONTH, 0)
endCal.set(Calendar.HOUR, 0)
endCal.set(Calendar.MINUTE, 0)
endCal.set(Calendar.SECOND, 0)
endCal.set(Calendar.MILLISECOND, 0)
# endCal.set(Calendar.YEAR, 2015)
# endCal.set(Calendar.MONTH, 11)

officeID = "SWF"

# the gateCalc object can perform its calculation for a single flow group
# the computeFlowGroup method takes:
# officeId
# projectId
# startDate
# endDate
# gateCalc.computeFlowGroup("SWF", "LEWT2",  startCal.getTime(), endCal.getTime(), "Flow.LEWT2.ConduitGate_Total")
# By setting the following parameter to True, the following flow groups in the list FlowGroupList will all be calculated. Items can be commented out
# or commented back in individually. To turn this option off, set the following parameter to False. User can determine which flow group they want to calculate
# by changing the "flowGroup" variable.
calculateSingleFlowGroups = True
flowGroupGate = "ConduitGate_Total"
flowGroupTotal = "Project_Total"
flowGroupTurbine = "Turbine_Total"
flowGroupPumpOutBelow = "Pump_Out_Below_Total"
flowGroupPumpOut = "Pump_Out_Total"
flowGroupPumpIn = "Pump_In_Total"
flowGroupUncontrol = "Uncontrolled_Total"
flowGroupNTMWD = "Pump_NTMWD"
flowGroupUTRWD = "Pump_UTRWD"
flowGroupSS= "Pump_Sulphur_Springs"
flowGroupIrving = "Pump_Irving"
flowGroupLewisville = "Lewisville"
flowGroupUTRWD_Out = "UTRWD_Out"
flowGroupUTRWD_In = "UTRWD_In"
flowGroupIrv = "Irving"
flowGroupDenton = "Denton"
flowGroupBenbrook = "Benbrook"
flowGroupTRWD = "TRWD"
flowGroupWeatherford = "Weatherford"
flowGroupGeorgetown = "Georgetown"
flowGroupRound_Rock = "Round_Rock"
flowGroupBrushy_Ck = "Brushy_Ck"
flowGroupNTMWD_LVN = "NTMWD"
flowGroupCooper = "Cooper"
flowGroupEast_Fork = "East_Fork"
flowGroupTawakoni = "Tawakoni"


locationList = ["BNBT2",
                "GGLT2",
                "LEWT2",
                "LVNT2",
                "SCLT2"
                ]

# the calculation can also be performed for all the associated groups
# the computeAll method takes:
# officeId
# projectId
# startDate
# endDate
# By setting the following parameter to True, all of the following flow groups in each location in the list locationList will all be calculated.
# Items can be commented out or commented back in individually. To turn this option off, set the following parameter to False.

calculateAllFlowGroups = False
FlowGroupList = ["BNBT2",
                "GGLT2",
                "LEWT2",
                "LVNT2",
                "SCLT2"
                ]


if calculateSingleFlowGroups:
    for location in locationList:
        print "Now Running", location, "SINGLE"
        #compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupGate)
        #compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupTotal)
        #compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupTurbine)
        #compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupUncontrol)
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupPumpOutBelow)
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupPumpOut)
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupPumpIn)
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupNTMWD)
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupUTRWD) 
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupSS)
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupIrving) 
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupLewisville)
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupUTRWD_Out)
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupUTRWD_In)
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupIrv)
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupDenton)
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupBenbrook)
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupTRWD)
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupWeatherford) 
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupGeorgetown)
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupRound_Rock) 
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupBrushy_Ck)
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupNTMWD_LVN)
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupCooper) 
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupEast_Fork) 
        compute_Single_Flowgroup(officeID, location, startCal, endCal, flowGroupTawakoni)
if calculateAllFlowGroups:
    for location in FlowGroupList:
        print "Now Running", location, "GROUP"
        #compute_All_Flowgroups(officeID, location, startCal, endCal)



