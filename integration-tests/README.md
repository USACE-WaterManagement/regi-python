# CDA integration tests

Docker-based integration tests that spin up a real CWMS database + CDA
(`cwms-data-api`) instance, seed it via `cda-etl`, and run tests against it --
as opposed to the JPype/reflection-based unit and smoke tests under
[`regi-headless/src/test/python/`](../regi-headless/src/test/python/).

The stack is defined in [`docker-compose.yml`](docker-compose.yml), adapted
from the `cwms-data-api` repo's own compose file for automated testing from
regi-python: `data-api` runs from a pre-built image, and `cda-etl` is built
from the CDA GitHub repo by compose. Tests authenticate with a CWMS API key
(see [`conftest.py`](conftest.py)).

[`test_environment.py`](src/test/python/test_environment.py) covers
infra-only: bringing the stack up healthy and seeded.
[`test_inflow_calc.py`](src/test/python/test_inflow_calc.py),
[`test_gate_flow_calc.py`](src/test/python/test_gate_flow_calc.py), and
[`test_gate_settings_calc.py`](src/test/python/test_gate_settings_calc.py)
exercise `regi_python`/`run_headless` against the seeded data -- one
calculation family each, matching the three scriptable calculations
[`district-scripts/`](../district-scripts/) uses (Inflow, Gate Flow, Gate
Settings). See "Calculation tests" below for how they're structured.

## Prerequisites

1. **Docker**, with the `docker compose` CLI plugin, running locally.
2. **Images.** `data-api` pulls `ghcr.io/usace/cwms-data-api`; the tag is
   pinned in [`docker-compose.yml`](docker-compose.yml) (not `latest`, so runs
   are reproducible) and can be overridden via `CDA_DATA_API_VERSION`.
   `cda-etl` (and `cda-expander`) are built by Docker directly from
   `https://github.com/USACE/cwms-data-api.git` (subdir `cda-etl`) at the ref
   pinned in the same file, and tagged `cwms-data-api/etl:local` -- no
   published image is needed. Copy [`.env.example`](.env.example) to `.env` to
   override `CDA_DATA_API_VERSION`, `CDA_ETL_GIT_URL` and `CDA_ETL_GIT_REF`
   (set `develop` to track latest). The build needs network access to
   github.com and PyPI. To build manually: `docker compose build cda-etl`.
3. **Config and seed data**, vendored in this repo under
   [`compose_files/`](compose_files/):
   - [`compose_files/sql/`](compose_files/sql/) (SQL grant script for the web
     user)
   - [`compose_files/regi-data/`](compose_files/regi-data/) (the REGI ETL
     config -- [`regi.yml`](compose_files/regi-data/regi.yml),
     [`regi.templates.yml`](compose_files/regi-data/regi.templates.yml), and
     the expander-generated
     [`regi.generated.yml`](compose_files/regi-data/regi.generated.yml) --
     plus the seed data files under
     [`SWT/`](compose_files/regi-data/SWT/) that it references)
4. Python deps: `pip install -r requirements.txt`
   ([`requirements.txt`](requirements.txt)) -- includes `cwms-python`, which
   the calculation tests use to read/write CDA data (see "Calculation tests"
   below) instead of hand-rolled `requests` calls.
5. The `regi_python` wheel built by `:regi-headless`
   ([`regi-headless/`](../regi-headless/)), installed into the same
   environment -- the calculation tests run `regi_python` against the seeded
   CDA data.

## Running

Directly with a local `pytest` install (build and install the wheel first):

```
../gradlew :regi-headless:buildPythonWheel
pip install ../regi-headless/build/install/regi_python/dist/*.whl
pip install -r requirements.txt
pytest -m integration
```

Or via Gradle, using the same Gradle-managed Python venv approach
(`com.pswidersk.python-plugin` + `VenvTask`) as
[`regi-headless/build.gradle`](../regi-headless/build.gradle) (this module's
task is in [`build.gradle`](build.gradle)):

```
./gradlew :integration-tests:integrationTest
```

The `cda_stack` fixture (in [`conftest.py`](conftest.py)) runs `docker compose up --wait`
for `db` and `data-api` (`db_webuser_permissions` runs first as a one-shot
job), then runs `cda-etl` once as a seeding step via
`docker compose --profile seed run --build --rm cda-etl` (it's gated behind the
`seed` profile so a plain `up` doesn't try to start it as a long-running
service). The stack is torn down at the end of the session.

Because these tests only run when explicitly selected (`-m integration`), a
missing prerequisite (Docker, the `regi_python` wheel, `cwms-python`) or a
stack that can't be brought up fails the session with an explanatory message
instead of skipping. Set `CDA_COMPOSE_LOG` to a file path to have the
fixture write the compose containers' logs there before it tears the stack
down.

If you've already brought the stack up yourself (`docker compose up --wait
db data-api && docker compose --profile seed run --rm cda-etl`), the
`cda_stack` fixture can skip managing docker compose altogether -- no
`compose.start()`/`compose.stop()`, no reseed -- and just point tests at
what's already running. This avoids both the compose bring-up wait and the
forced Oracle reinit that `compose.stop()` otherwise causes on every session
teardown (`db` has no persistent volume, so a teardown throws away its
initialized state and the next run needs a full ETL reseed).

Running directly with `pytest`, set the env var (its mere presence enables
the bypass -- there's no separate on/off flag):

```
CDA_EXTERNAL_STACK_URL=http://localhost:7000/cwms-data/ CWMS_TEST_API_KEY=<your-stack's-key> pytest -m integration
```

Running via the `integrationTest` Gradle task, use `-P` properties instead
(these are re-read fresh on every invocation, unlike env vars, which an
already-running Gradle daemon may not see) -- `integrationTest` forwards them
to the `CDA_EXTERNAL_STACK_URL`/`CWMS_TEST_API_KEY` env vars above:

```
./gradlew :integration-tests:integrationTest -Ptestcontainer.cwms.bypass.url=http://localhost:7000/cwms-data/ -Ptestcontainer.cwms.bypass.apiKey=<your-stack's-key>
```

## Remote debugging the embedded JVM

`regi_python`'s `regi_session()`
([`regi_python.py`](../regi-headless/src/main/python/regi_python/regi_python.py))
can start the embedded JVM with a JDWP agent
so IntelliJ (or any JDWP-capable debugger) can attach to it and step through
`:regi-headless` and any of its compiled dependencies (e.g. the
`mil.army.usace.hec.serversuite.cda.*` login classes).

Enable it via `gradle.properties` (same mechanism as the CDA bypass
properties above; see [`gradle.properties.template`](../gradle.properties.template))
-- uncomment/add:

```
regiHeadless.debug.port=5005
regiHeadless.debug.suspend=y
```

Then run `./gradlew :integration-tests:integrationTest` as usual.
`suspend=y` blocks the JVM (and so the whole pytest session) at startup until
a debugger attaches -- with the docker-compose bypass in place, that's the
first thing that happens, so there's no race to attach in time. Set
`regiHeadless.debug.suspend=n` instead to let the JVM start immediately and
only pause once an actual breakpoint is hit.

In IntelliJ: **Run > Edit Configurations > + > Remote JVM Debug**, host
`localhost`, port `5005` (matching `regiHeadless.debug.port`), then start it
in debug mode before (or, with `suspend=n`, any time during) the Gradle run.
Make sure the `:regi-headless` module (and any attached sources for its
compiled dependencies) is part of that run configuration's classpath so
breakpoints resolve.

Leave both properties commented out for normal runs -- an open debug port
with `suspend=y` will hang any automated/CI invocation waiting for a
debugger that never attaches.

## Calculation tests

[`test_inflow_calc.py`](src/test/python/test_inflow_calc.py),
[`test_gate_flow_calc.py`](src/test/python/test_gate_flow_calc.py), and
[`test_gate_settings_calc.py`](src/test/python/test_gate_settings_calc.py)
all follow the same shape:

1. Run a real calculation (through `regi_python`'s `run_headless`, via the
   session-scoped `run_regi_calculation` fixture in
   [`conftest.py`](conftest.py)) against data seeded by
   [`regi.yml`](compose_files/regi-data/regi.yml).
2. Fetch the timeseries the calculation just wrote from CDA, via
   [`regi_calc_support.fetch_timeseries`](src/test/python/regi_calc_support.py) -- a thin wrapper around
   `cwms.get_timeseries()` from [`cwms-python`][cwms-python], not a
   hand-rolled REST call. It depends on the session-scoped `cwms_session`
   fixture in `conftest.py`, which points `cwms.init_session()` at the
   seeded stack once for the whole session (cwms-python keeps its
   connection/auth as module-level state, not an object passed around).
3. Compare it against a "known-good" reference timeseries, using
   `regi_calc_support.assert_timeseries_matches` (small relative/absolute
   floating-point tolerance; exact timestamp alignment).

[cwms-python]: https://github.com/HydrologicEngineeringCenter/cwms-python

### Known-good reference series

There's no separate structure in [`regi.yml`](compose_files/regi-data/regi.yml) for "the expected answer" --
instead, a reference series is seeded as a perfectly ordinary timeseries
entry under the same location/parameter the calculation writes to, but
tagged with the version token `REGI-Test-Expected` instead of a real REGI/CWMS
version (e.g. `EUFA.Flow-Res In.Ave.~1Day.1Day.REGI-Test-Expected`, next to the
`Regi-Rev-Adjusted` version the Inflow calculation actually writes). Nothing
ever computes into a `REGI-Test-Expected` series; it exists purely as this test
suite's frozen comparison target, and its seed file under
[`compose_files/regi-data/SWT/Timeseries/`](compose_files/regi-data/SWT/Timeseries/)
is a plain data file like any other.

For [`test_inflow_calc.py`](src/test/python/test_inflow_calc.py), that reference was created by freezing a few days
of the *real, already-seeded* historical output of `Regi-Rev-Adjusted`
(itself production data) into a `REGI-Test-Expected` copy, before ever running
the calculation against it. Since the calculation's other inputs for that
window (elevation, storage, project release, evaporation) are also
unchanged historical data, recomputing over the same window should
reproduce the same output -- this is what the test asserts. Building a new
case this way, for a different calculation or project, means:

1. Find the ts id the calculation under test actually writes (check the
   `LOCATION TIME SERIES ASSOCIATION` properties for the relevant
   `Regi_*_OUTPUT`/`Regi_*_PRIMARY` key, in
   [`compose_files/regi-data/SWT/Properties/`](compose_files/regi-data/SWT/Properties/)).
2. Pick a comparison window fully inside the seeded period of record,
   away from either edge.
3. Copy that ts id's currently-seeded values for the window into a new
   `...REGI-Test-Expected` seed file (same shape, different `name`/version).
4. Add the new id to the project's `timeseries:` list in
   [`regi.yml`](compose_files/regi-data/regi.yml).
5. Write the test: run the calculation, fetch both series, compare.

If no seeded historical output already exists for what you're testing,
running the calculation once against real/trusted data and manually
verifying its output is correct -- then freezing *that* as the
`REGI-Test-Expected` reference -- works the same way.
