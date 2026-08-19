from regi_python import regi_session, run_headless


def run_calculations(registry):
    from datetime import datetime, timedelta, timezone
    from zoneinfo import ZoneInfo

    # Java imports must happen after regi_session starts the JVM.
    from usace.rowcps.headless import LoggingOptions


    def compute_All_Flowgroups(officeID, location, start_date, end_date):
        # Takes in locations defined by user in group and computes all flow groups
        try:
            gateCalc.computeAll(officeID, location, start_date, end_date)
        except Exception as e:
            print("Error Computing all Flow Groups at {0} {1}".format(officeID, location))
            print(e)
            print('')


    def compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroup):
        try:
            gateCalc.computeFlowGroup(officeID, location, start_date, end_date, "Flow.{0}.{1}".format(location, flowGroup))
        except Exception as e:
            print("Error Computing Flow Group {0} at {1}".format(officeID, location))
            print(e)
            print('')

        # #gateCalc.computeFlowGroup("SWF", "ACTT2",  start_date, end_date, "Flow.ACTT2.Pump_Out_Total")
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

    # Time zone must be set explicitly because the JVM's default timezone is
    # UTC, not the district's local time. (The previous Calendar.getInstance()
    # calls here had no explicit timezone and silently depended on whatever
    # timezone the host happened to be configured with.)
    central = ZoneInfo("America/Chicago")
    today_midnight = datetime.now(central).replace(hour=0, minute=0, second=0, microsecond=0)

    # start: yesterday, at midnight
    start_date_dt = today_midnight - timedelta(days=1)
    # end: today, at midnight
    end_date_dt = today_midnight

    start_date = start_date_dt.astimezone(timezone.utc)
    end_date = end_date_dt.astimezone(timezone.utc)

    officeID = "SWF"

    # the gateCalc object can perform its calculation for a single flow group
    # the computeFlowGroup method takes:
    # officeId
    # projectId
    # startDate
    # endDate
    # gateCalc.computeFlowGroup("SWF", "LEWT2",  start_date, end_date, "Flow.LEWT2.ConduitGate_Total")
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
            print("Now Running", location, "SINGLE")
            #compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupGate)
            #compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupTotal)
            #compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupTurbine)
            #compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupUncontrol)
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupPumpOutBelow)
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupPumpOut)
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupPumpIn)
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupNTMWD)
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupUTRWD) 
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupSS)
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupIrving) 
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupLewisville)
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupUTRWD_Out)
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupUTRWD_In)
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupIrv)
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupDenton)
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupBenbrook)
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupTRWD)
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupWeatherford) 
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupGeorgetown)
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupRound_Rock) 
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupBrushy_Ck)
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupNTMWD_LVN)
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupCooper) 
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupEast_Fork) 
            compute_Single_Flowgroup(officeID, location, start_date, end_date, flowGroupTawakoni)
    if calculateAllFlowGroups:
        for location in FlowGroupList:
            print("Now Running", location, "GROUP")
            #compute_All_Flowgroups(officeID, location, start_date, end_date)





if __name__ == "__main__":
    with regi_session():
        run_headless(run_calculations)
