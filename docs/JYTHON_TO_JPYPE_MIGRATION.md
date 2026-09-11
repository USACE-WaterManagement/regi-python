# Migrating REGI Headless District Jython Scripts to `regi_python`

This guide captures the script migration pattern used in the district-scripts history, 
moving from old Python 2 Jython-style top-level scripts to the current JPype-based `regi_python` bridge.

### Callback Mechanism
The key mental shift is that your script no longer procedurally runs from top to bottom. 
Instead, you define your calculation logic inside a function – a callback – and hand that function to `run_headless()`. 
The REGI framework starts the JVM, prepares the execution environment, and then calls your callback. 
The top level of your script only needs to define and hand off the callback. 

## Core Migration Pattern

Old scripts typically:

- imported Java classes at module import time
- accessed global `registry` and calculation objects at top level
- executed the calculation immediately when the file was loaded
- relied on shell wrappers such as `RunHeadlessJython.bat` or `.sh`

New scripts should:

- import `regi_session` and `run_headless` from `regi_python`
- move Java imports inside a callback, such as `run_calculations(registry)` below, which `run_headless` invokes once the JVM has started
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
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo

    gateCalc = registry.getCalculation(1.0, "Gate Flow")

    central = ZoneInfo("America/Chicago")
    start_date = datetime(2015, 5, 1, tzinfo=central).astimezone(timezone.utc)
    end_date = datetime(2015, 7, 1, tzinfo=central).astimezone(timezone.utc)
    gateCalc.computeFlowGroup("SWT", "FOSS", start_date, end_date, "Flow.FOSS.Project_Total")


if __name__ == "__main__":
    with regi_session():
        run_headless(run_calculations)
```

Note that this example no longer imports anything from `java.util` at all. Date/time
values are built entirely in Python and only cross into Java as plain `datetime`
objects — see [Date and Time Handling](#date-and-time-handling) below.

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

### 7. Replace `java.util.Calendar`/`TimeZone` with `datetime`/`zoneinfo`

Old scripts built `java.util.Date` objects with `Calendar.getInstance(TimeZone.getTimeZone(...))`.
New scripts should build ordinary Python `datetime` objects with `zoneinfo.ZoneInfo` instead,
and pass them straight into the Java call. See
[Date and Time Handling](#date-and-time-handling) for the full pattern and the one
timezone rule you must not skip.

## Date and Time Handling

The Scriptable calculation APIs (`ScriptableInflow`, `ScriptableGateSettings`,
`ScriptableGateFlowCalc`) accept `java.time.Instant` parameters for start/end dates.
(The old `java.util.Date`/`long` overloads still exist but are `@Deprecated` —
prefer `Instant`.) JPype automatically converts a plain Python `datetime.datetime`
into a Java `Instant` when the target parameter is declared as `Instant`, so **you
do not need to construct any Java object yourself**. Build the date in Python and
pass it directly:

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

central = ZoneInfo("America/Chicago")
start_date = datetime(2018, 8, 1, tzinfo=central).astimezone(timezone.utc)
```

### The one rule: always convert to UTC before calling into Java

JPype's automatic `datetime -> Instant` conversion does **not** look at the
`tzinfo` on the value you pass — it takes whatever wall-clock fields the datetime
has and treats them as if they were already UTC. If you hand it a
timezone-aware-but-not-UTC datetime directly, you will get the wrong instant with
no error or warning:

```python
central = ZoneInfo("America/Chicago")
midnight_central = datetime(2015, 5, 1, tzinfo=central)   # 2015-05-01 00:00 CDT == 2015-05-01 05:00 UTC

gateCalc.computeAll("SWF", "LEWT2", midnight_central, end_date)   # WRONG: silently treated as 00:00 UTC, 5 hours off
```

Always call `.astimezone(timezone.utc)` on the value before it crosses into a
Java call, as shown in every example in this document. Once a datetime's wall
clock actually represents UTC, JPype's conversion is exact and this is the only
step required — no epoch-millis math, no manual `Instant` construction.

This is also why the timezone must always be given explicitly with
`zoneinfo.ZoneInfo("America/Chicago")` (or whatever the district's local zone
is) rather than left off. The JVM's own default timezone is UTC, not the
district's local time — a naive `datetime.now()` or a `datetime` built without
`tzinfo` has no way to know it should mean "Central time," and some
scripts that called `Calendar.getInstance()` with no `TimeZone` argument were
silently relying on whatever timezone the host machine happened to have
configured. Always pass `tzinfo=` explicitly when constructing the date.

### Building relative dates ("N days ago", "top of the hour", etc.)

Most district scripts compute a date relative to "now" rather than a fixed date.
Use `datetime.now(tz)` plus `timedelta` arithmetic, then `.replace(...)` to zero
out whichever fields need truncating — this mirrors what `Calendar.add()` /
`Calendar.set()` used to do, and is safe across DST transitions the same way:

```python
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

central = ZoneInfo("America/Chicago")

# "5 days ago at midnight" through "tomorrow at midnight"
today_midnight = datetime.now(central).replace(hour=0, minute=0, second=0, microsecond=0)
start_date = (today_midnight - timedelta(days=5)).astimezone(timezone.utc)
end_date = (today_midnight + timedelta(days=1)).astimezone(timezone.utc)

# "5 days ago at the top of the current hour" through "the top of the current hour"
end_date_dt = datetime.now(central).replace(minute=0, second=0, microsecond=0)
start_date_dt = end_date_dt - timedelta(days=5)
start_date = start_date_dt.astimezone(timezone.utc)
end_date = end_date_dt.astimezone(timezone.utc)
```

A couple of translation notes when porting the old `Calendar` field calls:

| Old `Calendar` code | `datetime` equivalent |
| --- | --- |
| `cal.add(Calendar.DAY_OF_MONTH, -5)` | `dt - timedelta(days=5)` |
| `cal.set(Calendar.HOUR_OF_DAY, 0)` + `MINUTE`/`SECOND`/`MILLISECOND` to `0` | `dt.replace(hour=0, minute=0, second=0, microsecond=0)` |
| `cal.set(Calendar.MONTH, 4)` | `dt.replace(month=5)` — **`Calendar.MONTH` is 0-indexed** (4 == May); `datetime.month` is 1-indexed, so add 1 when porting a literal month value |
| `cal.set(Calendar.HOUR, 0)` | Avoid porting this one directly — `Calendar.HOUR` is the 12-hour field and doesn't reliably mean midnight (it depends on the AM/PM already set on the calendar). Use `hour=0` on the `datetime`, which unambiguously means midnight. |

### Using the `long` epoch-millis overloads

`ScriptableGateFlowCalc.computeAll`/`computeFlowGroup` also has `long` (epoch
milliseconds) overloads. These remain valid but are deprecated in favor of
`Instant`; if you do need a raw millisecond value, get it from an
already-UTC-normalized datetime: `int(start_date.timestamp() * 1000)`.

## Project-Specific Examples

The current district scripts show the same migration shape across several script families:

- `SWF/InflowCalcComputedInflow.py`
- `SWF/InflowCalcComputeEvapAsFlow.py`
- `SWF/GateSettings.py`
- `SWT/GateFlowGroup1.py`
- `SWL/Big3-GateFlow.py`

The differences between them are the calculation names, location lists, and optional logging or flow-group loops. The migration pattern itself is the same.
