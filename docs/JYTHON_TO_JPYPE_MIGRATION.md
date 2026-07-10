# Migrating REGI Headless District Jython Scripts to `regi_python`

This guide captures the script migration pattern used in the district-scripts history, 
moving from old Python 2 Jython-style top-level scripts to the current JPype-based `regi_python` bridge.

## Core Migration Pattern

Old scripts typically:

- imported Java classes at module import time
- accessed global `registry` and calculation objects at top level
- executed the calculation immediately when the file was loaded
- relied on shell wrappers such as `RunHeadlessJython.bat` or `.sh`

New scripts should:

- import `regi_session` and `run_headless` from `regi_python`
- move Java imports inside a callback that runs after the JVM starts
- wrap the calculation logic in a function such as `run_calculations(registry)`
- keep `registry.getCalculation(...)` and Java method calls unchanged
- end with `if __name__ == "__main__": with regi_session(): run_headless(run_calculations)`

## Before And After

### Before

```python
from java.util import Calendar
from java.util import TimeZone

gateCalc = registry.getCalculation(1.0, "Gate Flow")
timeZone = TimeZone.getTimeZone("US/Central")
startCal = Calendar.getInstance(timeZone)
endCal = Calendar.getInstance(timeZone)
gateCalc.computeFlowGroup("SWT", "FOSS", startCal.getTime(), endCal.getTime(), "Flow.FOSS.Project_Total")
```

### After

```python
from regi_python import regi_session, run_headless


def run_calculations(registry):
    from java.util import Calendar
    from java.util import TimeZone

    gateCalc = registry.getCalculation(1.0, "Gate Flow")
    timeZone = TimeZone.getTimeZone("US/Central")
    startCal = Calendar.getInstance(timeZone)
    endCal = Calendar.getInstance(timeZone)
    gateCalc.computeFlowGroup("SWT", "FOSS", startCal.getTime(), endCal.getTime(), "Flow.FOSS.Project_Total")


if __name__ == "__main__":
    with regi_session():
        run_headless(run_calculations)
```

## Translation Rules

### 1. Move Java imports inside the callback

JPype-backed imports should happen after the JVM starts. 
Put them inside `run_calculations(registry)` or a nested helper only called from that callback.

This is the biggest behavioral difference from Jython scripts.

### 2. Keep the registry lookup pattern

The migration does not change the scriptable REGI API. Calls like these stay the same:

- `registry.getNames(1.0)`
- `registry.getCalculation(1.0, "Inflow")`
- `registry.getCalculation(1.0, "Gate Flow")`

The change is only the Python wrapper around those calls.

### 3. Convert top-level execution into a callback

Scripts must be converted from immediate execution to a `run_calculations()` function. 
That keeps import side effects out of the module.

### 4. Replace Python 2 `print` statements

Old scripts often contain lines like:

```python
print "Error Computing Flow Group"
```

Update these to Python 3 syntax:

```python
print("Error Computing Flow Group")
```

### 5. Keep optional Java-side logging calls

Calls such as `LoggingOptions.setDbMessageLevel(2)` and `LoggingOptions.setMetricsEnabled(True)` still belong in the script if the district workflow depends on them. They do not move to `regi_python`; they simply live inside the callback now.

### 6. Remove the shell wrapper

The old `RunHeadlessJython` launchers are no longer needed. The Python file itself becomes the entry point:

```python
if __name__ == "__main__":
    with regi_session():
        run_headless(run_calculations)
```

## Project-Specific Examples

The current district scripts show the same migration shape across several script families:

- `SWF/InflowCalcComputedInflow.py`
- `SWF/InflowCalcComputeEvapAsFlow.py`
- `SWF/GateSettings.py`
- `SWT/GateFlowGroup1.py`
- `SWL/Big3-GateFlow.py`

The differences between them are the calculation names, location lists, and optional logging or flow-group loops. The migration pattern itself is the same.
