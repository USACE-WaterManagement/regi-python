from regi_python import regi_session, run_headless


def run_calculations(registry):
    from datetime import datetime, timedelta, timezone
    from zoneinfo import ZoneInfo

    # Java imports must happen after regi_session starts the JVM.
    from usace.rowcps.headless.calculator.inflow import InflowComputationStorageOption


    # this gets a ScriptableInflow instance.
    inflowCalc = registry.getCalculation(1.0, "Inflow")

    # configure the start/end dates
    ##central = ZoneInfo("America/Chicago")
    ##start_date = (datetime(2019, 2, 1, tzinfo=central)).astimezone(timezone.utc)
    ##end_date = (datetime(2019, 2, 4, tzinfo=central)).astimezone(timezone.utc)

    central = ZoneInfo("America/Chicago")
    today_midnight = datetime.now(central).replace(hour=0, minute=0, second=0, microsecond=0)

    # start: 4 days ago, at midnight
    start_date = (today_midnight - timedelta(days=4)).astimezone(timezone.utc)
    # end: tomorrow, at midnight
    end_date = (today_midnight + timedelta(days=1)).astimezone(timezone.utc)

    # inflowCalc includes a setComputationStorageOptions function, which takes in either one or many
    # InflowComputationStorageOption values.  This is used by computeInflow to determine if it should save additional
    # computed values like evaporation as flow and project releases.
    # 
    # The InflowComputationStorageOption enum contains two values:
    #   EVAP_AS_FLOW
    #   PROJECT_RELEASES
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
        inflowCalc.computeInflow("SWF", loc, start_date, end_date)


if __name__ == "__main__":
    with regi_session():
        run_headless(run_calculations)
