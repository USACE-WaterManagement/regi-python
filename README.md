# REGI-Headless

> [!IMPORTANT]
> **Notice: Project Refactor in Progress**
> This project is undergoing a large refactor for [CWMS Data API](https://github.com/USACE/cwms-data-api) support. 
> It will transition from a Java project consuming Jython scripts to a **Python project** that 
> utilizes **JPype** to call underlying REGI Java libraries.

`REGI-Headless` provides a Python-based interface for running **REGI** calculations in a headless environment. It allows users to execute complex hydrological calculations and manage gate settings via Python scripts, leveraging the performance and stability of the original REGI Java libraries.

## Features

- **Headless Execution**: Run REGI calculations as part of automated workflows, CI/CD pipelines, or on servers.
- **Python-First API**: Write calculation scripts in standard Python 3.
- **Java Interoperability**: Direct access to REGI Java libraries via JPype.
- **Modular Calculations**: Full support for:
  - Inflow calculations (Clone, Compute, Auto-Adjust, Balance All, etc.)
  - Flow Group
  - Gate settings calculations.

## Project Structure

- `regi-headless/`: Core implementation.
  - `src/main/python/`: The `regi-python` package source.
  - `src/main/java/`: Java-based headless support and factories.
- `district-scripts/`: Legacy Jython scripts and district-specific configurations.
- `docs/`: Additional documentation.

## Getting Started

### Prerequisites

- Java JDK 21 or higher.
- **Python 3.11** or higher.

### CWMS Data API Configuration

The library reads the following environment variables when establishing the CWMS Data API data source:

- `CDA_URL`: Base URL for the CWMS Data API endpoint.
- `API_KEY`: API key used for CWMS Data API authentication and authorization.
- `OFFICE_ID`: CWMS office identifier used to scope the session.

The factory uses these values to authenticate, resolve the current user, and persist the connected office and time zone into the REGI project.

### Building

The project uses Gradle to manage both Java and Python builds. To build the Python wheel including all Java dependencies:

```powershell
./gradlew buildPythonWheel
```

The resulting wheel file will be located in `regi-headless/build/install/regi-python/dist/`.

## Usage

### Installation

Install the built wheel into your Python environment:

```powershell
pip install regi_python-*.whl
```

### Script Example

The Python bridge uses a context manager to handle the JVM lifecycle and a callback mechanism for calculations.

```python
from regi_python import regi_session, run_headless
from java.util import Calendar, TimeZone

def my_calculations(registry):
    # 'registry' is a RegiCalcRegistry instance
    gate_calc = registry.getCalculation(1.0, "Gate Flow")
    
    # Configure time window
    tz = TimeZone.getTimeZone("US/Central")
    start = Calendar.getInstance(tz)
    start.set(2025, 0, 1) # Jan 1, 2025
    
    end = Calendar.getInstance(tz)
    end.set(2025, 0, 2) # Jan 2, 2025
    
    # Execute calculation
    gate_calc.computeAll("OFFICE", "PROJECT", start.getTimeInMillis(), end.getTimeInMillis())

if __name__ == "__main__":
    with regi_session():
        run_headless(my_calculations)
```

### Environment Variables

- `JAVA_HOME`: Path to your Java installation (required for JPype).
- `REGI_LOG_LEVEL`: Logging level (e.g., `DEBUG`, `INFO`, `ERROR`).
- `CDA_URL`: URL for the CWMS Data API.
- `CDA_API_KEY`: API Key for CDA authentication.
- `OFFICE_ID`: Office ID for CDA authentication.

## Testing

To run the automated tests which build the wheel and execute a test script in a virtual environment:

```powershell
./gradlew testPythonWheel
```

## Maintainers

See [MAINTAINERS.md](MAINTAINERS.md) for a list of project maintainers.

## License

See [LICENSE](LICENSE) for licensing information.
