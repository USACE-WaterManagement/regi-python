# REGI-Headless

`regi-python` is a Python-first execution layer over the REGI Java libraries. The runtime bridge uses JPype to start the JVM, load the bundled REGI jars, and run Python callbacks against a Java-backed calculation registry.

## What Lives Where

- `regi-headless/src/main/python/regi_python/`
  - Python bridge code
  - Public entry points: `regi_session()` and `run_headless(calculation_callback)`
- `regi-headless/src/main/java/`
  - Java support layer used by the bridge calling into REGI calculation and data access libraries
- `district-scripts/`
  - Copy of district-owned Python scripts used as examples for smoke tests

## Requirements

- Java JDK 21 or higher
- Python 3.11 or higher

### Environment variables
- `JAVA_HOME` set for JPype startup
- `CDA_URL` url for CDA instance to connect to
- `CDA_API_KEY` required for accessing and storing data in CDA
- `OFFICE_ID` session scoped office for data access
- `REGI_LOG_LEVEL` for logging verbosity

## Building The Wheel

Build the Python wheel with Gradle:

```powershell
./gradlew buildPythonWheel
```

The wheel is written to `regi-headless/build/install/regi_python/dist/`.

Release tags become wheel versions and must be PEP 440 compatible. For example, use `0.0.2a0`, `0.0.2b0`, or `0.0.2rc0` instead of `0.0.2-alpha`, `0.0.2-beta`, or `0.0.2-rc`.

Install the built wheel into a Python environment:

```powershell
pip install regi_python-*.whl
```

## Releases

Releases are published from the GitHub repository at [USACE-WaterManagement/regi-python](https://github.com/USACE-WaterManagement/regi-python). A release build attaches the Python wheel and checksum file to the GitHub Release for the matching tag.

To consume a published wheel, download the wheel asset from the release and install it with your package manager. Use the exact wheel filename from the release asset URL.

```powershell
pip install https://github.com/USACE-WaterManagement/regi-python/releases/download/<tag>/regi_python-<version>-py3-none-any.whl
```

```powershell
uv pip install https://github.com/USACE-WaterManagement/regi-python/releases/download/<tag>/regi_python-<version>-py3-none-any.whl
```

```powershell
poetry add https://github.com/USACE-WaterManagement/regi-python/releases/download/<tag>/regi_python-<version>-py3-none-any.whl
```

```powershell
pdm add https://github.com/USACE-WaterManagement/regi-python/releases/download/<tag>/regi_python-<version>-py3-none-any.whl
```

If your tool does not support direct wheel URLs, download the asset from the release page and install it from the local `.whl` file instead.

## Using The Bridge

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


if __name__ == "__main__":
    with regi_session():
        run_headless(calculate_gate_flow)
```

`regi_session()` owns JVM startup and shutdown. `run_headless()` creates the REGI domain, invokes the callback with a `RegiCalcRegistry`, commits the session, and closes the domain when the callback finishes.

## Verification

Run the wheel smoke tests:

```powershell
./gradlew testPythonWheel
```

Run the script/API compatibility smoke test:

```powershell
./gradlew smokeTestDistrictScripts
```

`./gradlew check` runs both along with Java unit tests.

## Notes

- The Python package name is `regi_python`.
- The wheel metadata name is `regi-python`.
- The bundled Java jars are packaged inside `regi_python/lib/`.

## Maintainers

See [MAINTAINERS.md](MAINTAINERS.md).

## License

See [LICENSE](LICENSE).
