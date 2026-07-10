from regi_python import regi_session, run_headless


def calculate_inflow(registry):
    # Java imports must happen after regi_session starts the JVM.
    from java.util import Calendar, TimeZone

    # this gets a ScriptableInflow instance.
    inflow_calc = registry.getCalculation(1.0, "Inflow")

    # configure the start calendar
    start_cal = Calendar.getInstance(TimeZone.getTimeZone("US/Central"))
    start_cal.clear()
    start_cal.set(Calendar.YEAR, 2018)
    start_cal.set(Calendar.MONTH, 4)

    end_cal = Calendar.getInstance(TimeZone.getTimeZone("US/Central"))
    end_cal.clear()
    end_cal.set(Calendar.YEAR, 2018)
    end_cal.set(Calendar.MONTH, 4)
    end_cal.set(Calendar.DAY_OF_MONTH, 4)

    # This computes and saves evap as flow for EUFA in May 2018
    inflow_calc.computeEvapAsFlow("SWT", "EUFA", start_cal.getTime(), end_cal.getTime())


if __name__ == "__main__":
    with regi_session():
        run_headless(calculate_inflow)
