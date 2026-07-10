# AGENTS.md

## Repository Overview

`regi-headless` now uses a **Python-first execution model**.

- `regi-headless/src/main/python/regi_python` is the runtime bridge. It starts the JVM with **JPype** and exposes `regi_session()` and `run_headless(calculation_callback)`.
- `district-scripts/` and the example scripts under `regi-headless/src/test/resources/...` are now Python entrypoints that call into Java through the bridge.

Treat this repo as a Python orchestration layer over REGI Java libraries.

## Current Architecture

- `regi-headless/src/main/python/regi_python/regi_python.py` is the current Python entrypoint.
  - `regi_session()` owns JVM startup/shutdown.
  - `run_headless()` creates the REGI domain and invokes a Python callback with a Java-backed registry.
- `regi-headless/src/main/java/...` contains the Java support layer that the Python bridge calls through JPype.
- `district-scripts/` contains active district scripts written calling Java-backed calculations inside the callback.
- `regi-headless/src/test/resources/usace/rowcps/headless/examples` contains the same pattern for example scripts used by tests.

## File Groups To Treat Differently

- `regi-headless/src/main/python/`
  - python to java bridge code
  - prefer modern Python style and small, testable helpers
- `district-scripts/`
  - active district-owned operational scripts
  - preserve behavior unless the task explicitly changes calculation results or API usage
- `regi-headless/src/test/resources/usace/rowcps/headless/examples/`
  - example scripts used by tests
  - keep them aligned with the district-script pattern
- `docs/`
  - useful for historical context and documentation of features moving forward
  - `docs/agent-guides/` is the shared source of truth for agent-facing workflow guidance

## Working Rules

- Keep edits scoped to the requested migration target.
- When a script needs a new Java method, update the Java public API and the test harness together; the script test suite validates against the Java source-defined scriptable API.
- Avoid broad refactors outside the requested script family.

## Verification

Common checks in this repo:

- `./gradlew buildPythonWheel`
- `./gradlew testPythonWheel`

The Python package is built from `regi-headless/src/main/python`, and the wheel test verifies the package metadata, importability, public API exposure, and bundled Java jars.

## Environment Notes

The Python bridge expects the Java environment to be available, and the repo documentation currently references these variables:

- `JAVA_HOME`
- `CDA_URL`
- `CDA_API_KEY`
- `OFFICE_ID`
- `REGI_LOG_LEVEL`

Use the repo's current bridge code and tests as the source of truth for behavior; use the docs for orientation, not as a strict contract. `regi-headless/src/test/python/test_district_scripts.py` is the main contract for migrated script shape and allowed API calls.
