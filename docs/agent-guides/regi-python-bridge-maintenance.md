# REGI Python Bridge Maintenance

Use this guide when editing the Python bridge or troubleshooting runtime behavior.

## Focus files

- `regi-headless/src/main/python/regi_python/regi_python.py`
- `regi-headless/src/main/python/regi_python/regi_python_logging.py`

## Rules

- Start the JVM only inside `regi_session()`.
- Keep runtime-only JPype imports inside functions that run after JVM startup.
- Keep `run_headless(calculation_callback)` responsible for creating the domain, running the callback, committing, and shutting down cleanly.
- Keep Python logging and Java logging forwarding aligned.
- Keep wheel packaging and bundled jar checks working with the existing tests.

## Common checks

- `./gradlew buildPythonWheel`
- `./gradlew testPythonWheel`
