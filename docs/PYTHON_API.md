# REGI Python API

`regi_python` is the client-facing Python package for the REGI headless bridge. It is intentionally small: import the package, open a JVM session, and run your callback against a REGI registry.

## Package Surface

```python
from regi_python import regi_session, run_headless, __version__
```

- `regi_session()`: context manager that starts and stops the JVM for the bridge
- `run_headless(calculation_callback)`: executes a callback against a Java-backed registry
- `__version__`: installed package version, or `"unknown"` when the package is not installed from metadata

The package name on import is `regi_python`. The wheel metadata name is `regi-python`.

## Runtime Requirements

- Python 3.11 or newer
- Java JDK 21 or newer
- `JAVA_HOME` set before the bridge starts

The wheel bundles the REGI jars inside `regi_python/lib/`, and the bridge loads those jars at JVM startup.

## `regi_session()`

Use `regi_session()` as the outer lifecycle boundary for any bridge work.

Behavior:

- starts the JVM lazily if it is not already running
- configures Java logging to flow into Python logging
- shuts the JVM down when the context exits

Example:

```python
from regi_python import regi_session, run_headless

with regi_session():
    run_headless(my_callback)
```

Treat this context manager as the owner of the JVM lifecycle for the process.

### Nested and repeated calls

Only one JVM can ever exist in a Python process, and JPype cannot restart a JVM once it has been shut down. That gives `regi_session()` two rules:

- **The outermost call owns the JVM.** The first `regi_session()` entered in a process is the one that actually starts the JVM, and it is the only one that shuts it down. If you nest another `regi_session()` inside that still-open context, the nested call sees the JVM already running, does nothing on entry, and does nothing on exit -- it defers to the outer context. The JVM only shuts down when the *outermost* context exits.
- **A call after the first context has exited will fail.** Once the outermost `regi_session()` exits (and shuts the JVM down), that process cannot start a new JVM. A later, non-nested call to `regi_session()` -- one that opens after the first has already closed -- raises `RuntimeError` (wrapping JPype's `OSError`). Start a fresh process for each `regi_session()` you need; don't reopen one after a prior one has closed.

```python
with regi_session():        # starts the JVM; this is the owner
    with regi_session():    # JVM already running -> no-op start, no-op stop
        run_headless(my_callback)
    run_headless(my_other_callback)
# JVM shuts down here, when the outermost context exits

with regi_session():        # raises RuntimeError: a JVM cannot be restarted
    ...                      # in this process once it has been shut down
```

## `run_headless(calculation_callback)`

`run_headless()` creates a headless REGI domain and calls your callback with a `RegiCalcRegistry` instance.

Callback shape:

```python
def my_callback(registry):
    ...
```

Behavior:

- creates the REGI domain through `HeadlessRegiDomainFactory`
- builds a `RegiCalcRegistry` with the current manager id
- calls `calculation_callback(registry)`
- commits the domain only after the callback succeeds
- always shuts down the executor and closes the domain in `finally`
- logs the failure and re-raises any exception from the callback

The bridge is orchestration code. The callback is where client logic should live.

## Example

```python
from regi_python import regi_session, run_headless
from java.util import Calendar, TimeZone


def calculate_gate_flow(registry):
    gate_calc = registry.getCalculation(1.0, "Gate Flow")
    tz = TimeZone.getTimeZone("US/Central")
    start = Calendar.getInstance(tz)
    end = Calendar.getInstance(tz)
    start.set(2025, 0, 1)
    end.set(2025, 0, 2)
    gate_calc.computeAll("OFFICE", "PROJECT", start.getTimeInMillis(), end.getTimeInMillis())


with regi_session():
    run_headless(calculate_gate_flow)
```

## Logging

The bridge uses Python logging for client-visible output.

Environment variables:

- `REGI_LOG_LEVEL`: accepted Python log level name such as `DEBUG`, `INFO`, `WARNING`, or `ERROR`
- `REGI_LOG_FORMAT`: overrides the default Python log format
- `AWS_BATCH_JOB_ID` and `AWS_BATCH_JOB_ATTEMPT`: injected into the default log format when present

Java JUL records are forwarded into the same Python logger once the JVM starts.

## Compatibility

| Component | Supported |
| --- | --- |
| Python | 3.11+ |
| Java | JDK 21+ |
| Packaging | `regi-python` wheel with bundled jars |
| Import name | `regi_python` |

## Troubleshooting

- If JVM startup fails immediately, verify `JAVA_HOME` points at a JDK installation and not just a JRE.
- If imports fail after installation, confirm the wheel includes `regi_python/lib/*.jar` and that the package was installed from the built wheel.
- If logs do not appear, lower `REGI_LOG_LEVEL` or override `REGI_LOG_FORMAT`.
- If you are calling the package from a larger application, make sure some other code is not starting and stopping the JVM out from under `regi_session()`.
- If a second `regi_session()` call raises `RuntimeError: Failed to start the JVM for regi_session()...`, you opened it after an earlier, non-nested `regi_session()` had already exited and shut the JVM down in this process. Nest the call inside the still-open outer session instead, or run it in a fresh process.

