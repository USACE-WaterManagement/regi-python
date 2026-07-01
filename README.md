# REGI-Headless

> [!IMPORTANT]
> **Notice: Project Refactor in Progress**
> This project is undergoing a large refactor for CWMS Data API support. 
> It will transition from a Java project consuming Jython scripts to a **Python project** that 
> utilizes **JPype** to call underlying REGI Java libraries.

`REGI-Headless` is a Java-based command-line tool and library designed to run 
**REGI** calculations in a headless environment. 
It allows users to execute complex hydrological calculations and manage gate settings via Jython 
scripts without the need for a graphical interface.

## Features

- **Headless Execution**: Run REGI calculations as part of automated workflows or on servers.
- **Database Integration**: Connects to CWMS data retrieval and storage.
- **Modular Calculations**: Includes support for:
  - Inflow calculations (Clone, Compute, Auto-Adjust, Balance All, etc.)
  - Flow Group and gate settings calculations.

## Project Structure

- `regi-headless/`: Core Java implementation, including `RegiCLI`.
- `district-scripts/`: Example scripts and district-specific configurations.
- `docs/`: Additional documentation.

## Getting Started

### Prerequisites

- Java JDK 21 or higher.
- Access to a CWMS

### Building


```powershell
./gradlew build
```

Details TBD.

## Usage

TBD

### Command Line Options

TBD

### Example

TBD

## Testing

TBD

## Maintainers

See [MAINTAINERS.md](MAINTAINERS.md) for a list of project maintainers.

## License

See [LICENSE](LICENSE) for licensing information.