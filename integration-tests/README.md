# CDA integration tests

These tests run REGI calculations (Inflow, Gate Flow, Gate Settings) against a
throwaway copy of the CWMS database and Data API (CDA) that is loaded with
known data, then check the results against saved "expected" answers. They are
different from the unit and smoke tests under
[`regi-headless/src/test/python/`](../regi-headless/src/test/python/), which
don't talk to a database.

Pick the part that matches what you need:

- **[Writing and running tests](#part-1-writing-and-running-tests)** -- for
  engineers who work in Python: run the tests, add test cases, add seed data.
- **[How the harness works](#part-2-how-the-harness-works)** -- for developers
  who maintain the test stack, CI and upstream dependencies.

---

# Part 1: Writing and running tests

*For engineers who write Python and want to add test coverage. You do not need
to know how the Docker stack or the Java side works.*

## What a test does

1. A test copy of CWMS (an Oracle database plus the Data API) starts in
   Docker and is loaded with the sample data under
   [`compose_files/regi-data/`](compose_files/regi-data/).
2. The test runs a REGI calculation the same way your scripts in
   [`district-scripts/`](../district-scripts/) do (see
   [`docs/PYTHON_API.md`](../docs/PYTHON_API.md) for the calls available).
3. The test reads back the time series the calculation wrote and compares it
   with an **expected series** that is stored with the sample data. The test
   passes when every value in the expected series matches.

The expected series is just a normal time series whose version is
`REGI-Test-Expected` (for example
`EUFA.Flow-Power.Ave.1Hour.1Hour.REGI-Test-Expected`). Nothing computes into
it; it is the frozen, human-checked answer.

Before it runs, each test clears the output series it is about to check, so a
test cannot pass on old data left in the database.

## Running the tests

You need Docker running, internet access, and Java (the build downloads
everything else, including Python). From the repository root:

```
./gradlew :integration-tests:integrationTest
```

The first run is slow (tens of minutes): the database image has to start and
the sample data has to be loaded. Each test then takes about a minute.

### Running just one test, faster

Start the stack once, load the data once, and reuse it. From this directory:

```
docker compose up --wait db data-api
docker compose --profile seed run --build --rm cda-etl
```

Then, with the `regi_python` wheel and test requirements installed in your
Python environment:

```
../gradlew :regi-headless:buildPythonWheel
pip install ../regi-headless/build/install/regi_python/dist/*.whl
pip install -r requirements.txt
```

run any subset of the tests against the running stack:

```
CDA_EXTERNAL_STACK_URL=http://localhost:7000/cwms-data/ pytest -m integration -k KEYS
```

(`-k` matches part of a test name; `-m integration` is required.) When you
change sample data, rerun the `cda-etl` command above so the stack picks it
up. When you're done, `docker compose down` removes the stack.

## Adding a Gate Flow test

Each entry in `FLOW_GROUPS` in
[`test_gate_flow_calc.py`](src/test/python/test_gate_flow_calc.py) is one test.
Copy an existing entry and change it:

```python
"KEYS_TainterGate_Total": {
    "project_id": "KEYS",
    "flow_group_name": "Flow.KEYS.TainterGate_Total",
    "output_ts_id": "KEYS.Flow-RES-TGs.Ave.1Hour.1Hour.regi",
    "expected_ts_id": "KEYS.Flow-RES-TGs.Ave.1Hour.1Hour.REGI-Test-Expected",
    "calculation_start": datetime(2026, 6, 24, tzinfo=timezone.utc),
    "window_start": datetime(2026, 6, 25, tzinfo=timezone.utc),
    "window_end": datetime(2026, 6, 29, tzinfo=timezone.utc),
},
```

| Field | Meaning |
|---|---|
| `project_id` | Project to calculate. Optional; defaults to `EUFA`. |
| `flow_group_name` | The flow group, as `Flow.<PROJECT>.<Group>`. |
| `output_ts_id` | The series the calculation writes. Open the flow group's file in [`compose_files/regi-data/SWT/Clobs/`](compose_files/regi-data/SWT/Clobs/) (named `FLOW.<PROJECT>.<GROUP>.json`) and look in `<time_series_set>` for the `<time_series_id save_to_database="true">` entries; pick one and join its parts into `LOCATION.Parameter.Type.Interval.Duration.Version`. A flow group whose `<time_series_set>` is empty writes nothing and cannot be tested. |
| `expected_ts_id` | Same id with the version `REGI-Test-Expected`. You create it in [Adding or changing seed data](#adding-or-changing-seed-data). |
| `calculation_start` | Where the calculation starts. Optional; defaults to 2026-06-01. |
| `window_start`, `window_end` | The dates that are compared (end is exclusive). Optional; default to June 3 to June 7, 2026. Use a window where the inputs and the output both have data. |

Rules of thumb:

- The window must lie inside the data period loaded by the sample data
  (`startTime` in [`regi.yml`](compose_files/regi-data/regi.yml)), away from
  its edges.
- Choose a window where something actually happens. A flow group that is zero
  for the whole window proves very little; the FCOB case therefore uses
  hand-edited elevations (see the comment on that entry).

## Adding a test for another calculation

Copy [`test_inflow_calc.py`](src/test/python/test_inflow_calc.py) (a
time-series result) or
[`test_gate_settings_calc.py`](src/test/python/test_gate_settings_calc.py)
(gate-change records) and change the calculation call. The Inflow test is the
whole pattern:

```python
def test_auto_adjust_matches_known_good_inflow(run_regi_calculation, cwms_session):
    def calculate(registry):
        inflow_calc = registry.getCalculation(1.0, "Inflow")
        inflow_calc.autoAdjust(OFFICE_ID, PROJECT_ID, CALCULATION_START, False, False)

    run_regi_calculation(calculate)

    computed = fetch_timeseries(ADJUSTED_INFLOW_TS_ID, OFFICE_ID, WINDOW_START, WINDOW_END)
    expected = fetch_timeseries(EXPECTED_TS_ID, OFFICE_ID, WINDOW_START, WINDOW_END)
    assert expected, "the expected series didn't seed correctly"
    assert_timeseries_matches(computed, expected)
```

- `run_regi_calculation` runs your `calculate(registry)` function exactly as a
  district script's callback runs. It fails the test if REGI logs an error, so
  a calculation that quietly does nothing is caught.
- `fetch_timeseries` and `assert_timeseries_matches` live in
  [`regi_calc_support.py`](src/test/python/regi_calc_support.py). Values must
  match to a tiny tolerance, and the timestamps must line up exactly.
- Mark the test with `pytestmark = pytest.mark.integration`, as the existing
  files do; the tests only run when that marker is selected.

## Adding or changing seed data

All sample data lives under
[`compose_files/regi-data/`](compose_files/regi-data/):

| Where | What |
|---|---|
| [`SWT/Timeseries/`](compose_files/regi-data/SWT/Timeseries/) | One JSON file per time series, named by its id. |
| [`SWT/Clobs/`](compose_files/regi-data/SWT/Clobs/) | Flow group definitions (`FLOW.<PROJECT>.<GROUP>.json`). |
| [`SWT/Ratings/`](compose_files/regi-data/SWT/Ratings/) | Rating curves. |
| [`SWT/Outlets/`](compose_files/regi-data/SWT/Outlets/), [`Turbines/`](compose_files/regi-data/SWT/Turbines/), [`GateChanges/`](compose_files/regi-data/SWT/GateChanges/), [`TurbineChanges/`](compose_files/regi-data/SWT/TurbineChanges/) | Project structures and their change history. |
| [`SWT/LocationGroups/`](compose_files/regi-data/SWT/LocationGroups/), [`Properties/`](compose_files/regi-data/SWT/Properties/) | Groupings and the associations that tell REGI which series a calculation reads and writes. |

**A data file is only loaded if it is listed.** Two files control that, and
you must add the same entry to both:

- [`regi.yml`](compose_files/regi-data/regi.yml) -- the file people edit.
- [`regi.generated.yml`](compose_files/regi-data/regi.generated.yml) -- the
  file the loader reads. It is normally produced from `regi.yml` by a tool
  that needs access to a real CDA, so when you don't have one, add your entry
  to it by hand.

For example, to load a new series for a project, add it under that project's
`timeseries:` list in both files:

```yaml
timeseries:
  - id: EUFA.Flow-Power.Ave.1Hour.1Hour.REGI-Test-Expected
```

### Creating an expected series

If the series the calculation writes already has trustworthy data loaded for
your window, freeze a copy of it under the `REGI-Test-Expected` version. Run
this from this directory, changing the first four lines:

```python
import json
from datetime import datetime, timezone

source_id = "EUFA.Flow-Power.Ave.1Hour.1Hour.Rev-Regi-Flowgroup"  # the series the calculation writes
expected_id = source_id.rsplit(".", 1)[0] + ".REGI-Test-Expected"
begin = datetime(2026, 6, 3, tzinfo=timezone.utc)  # your comparison window
end = datetime(2026, 6, 7, tzinfo=timezone.utc)

folder = "compose_files/regi-data/SWT/Timeseries"
with open(f"{folder}/{source_id}.json", encoding="utf-8") as f:
    series = json.load(f)

ms = lambda dt: int(dt.timestamp() * 1000)
series["values"] = [v for v in series["values"] if ms(begin) <= v[0] < ms(end)]
series.update(name=expected_id, begin=begin.isoformat(), end=end.isoformat(),
              total=len(series["values"]))
series.pop("page", None)
series.pop("page-size", None)

with open(f"{folder}/{expected_id}.json", "w", encoding="utf-8") as f:
    json.dump(series, f, indent=2)
```

Then list the new id in `regi.yml` and `regi.generated.yml`, as above.

Copying output into the expected series only makes sense when that output is
already known to be right (for example, it is real historical production
data). If there is nothing to copy:

1. Run the calculation once and look at the result.
2. Check it by hand against something independent -- the inputs and the rating
   curve, a spreadsheet, a previous result.
3. Freeze the verified values as the expected series.

Do not freeze a result you haven't checked; the test would then only prove the
code still does what it did yesterday.

### Loading data from a real CDA

To pull real series, ratings and so on into the sample data, point the loader
at a CDA you can read:

1. Put `SOURCE_CDA_URL` and `SOURCE_CDA_API_KEY` in a `.env` file in this
   directory (start from [`.env.example`](.env.example)).
2. Add the ids you want to the project in `regi.yml`.
3. Regenerate the loader's file: `docker compose run --rm cda-expander`.
4. Run the loader: `docker compose --profile seed run --rm cda-etl`. When a
   source CDA is configured it downloads the listed items into
   `compose_files/regi-data/` before loading them.

The loader publishes time series for the window set by `startTime`/`endTime`
at the top of `regi.yml`.

## When a test fails

| You see | It means |
|---|---|
| `N value mismatch(es) (time: actual != expected)` | The calculation ran but produced different numbers. Compare the two columns; decide whether the code or the expected series is wrong. |
| `N expected timestamp(s) missing from computed output` | The calculation didn't write those times -- often the window is outside the inputs' data, or the calculation didn't run. |
| `REGI logged error(s) during the calculation` | REGI hit an error and logged it instead of stopping. The message is shown; the full log is `regi-projects/regi-python/regi-python.log` in this directory. |
| `Could not bring up the CDA docker stack` | Docker isn't running or can't pull images, or the stack didn't become healthy. Docker's own output is included in the message. |

---

# Part 2: How the harness works

*For developers who maintain the stack, the fixtures, CI and the upstream
dependencies.*

## Layout

| Path | Purpose |
|---|---|
| [`docker-compose.yml`](docker-compose.yml) | The stack: `db`, `db_webuser_permissions`, `data-api`, `cda-expander`, `cda-etl`. |
| [`conftest.py`](conftest.py) | Session fixtures: stack, clients, JVM, calculation runner. |
| [`src/test/python/`](src/test/python/) | Tests and [`regi_calc_support.py`](src/test/python/regi_calc_support.py). |
| [`compose_files/`](compose_files/) | Grant SQL ([`sql/`](compose_files/sql/)) and the REGI sample data ([`regi-data/`](compose_files/regi-data/)). |
| [`build.gradle`](build.gradle) | The `integrationTest` task (Gradle-managed Python venv, wheel install). |
| [`.env.example`](.env.example) | Overridable image tag, ETL source and ref, port. |
| [`../.github/workflows/integration-tests.yml`](../.github/workflows/integration-tests.yml) | CI job. |

## The stack

[`docker-compose.yml`](docker-compose.yml) is adapted from the
`cwms-data-api` repository's own compose file. `data-api` runs a published
image; `cda-etl` and `cda-expander` are built by Docker from the CDA GitHub
repository (subdirectory `cda-etl`) at a pinned ref and tagged
`cwms-data-api/etl:local`, so no published ETL image is needed (the build
needs network access to GitHub and PyPI).

- **Version pins** are the defaults in `docker-compose.yml`, documented in
  [`.env.example`](.env.example) (copy it to `.env` to override
  `CDA_DATA_API_VERSION`, `CDA_ETL_GIT_URL`, `CDA_ETL_GIT_REF`). Pin both to a
  tag or full commit SHA -- Docker's git build context does not accept an
  abbreviated SHA -- and keep the `data-api` tag and the ETL ref in step.
  Java dependency versions live in
  [`../gradle/libs.versions.toml`](../gradle/libs.versions.toml).
- **Authentication** is a CWMS API key (`CWMS_TEST_API_KEY`, with a
  test-stack default in `conftest.py`) through CDA's key access provider.
- **The `db` healthcheck must log in to the `FREEPDB1` service** (a `sqlplus`
  `select 1`), not just `tnsping` it. `tnsping` only proves the listener
  answers, which is true about 45 seconds before the database opens. If
  `data-api` starts in that window its connection pool fails with
  `ORA-12514: Service FREEPDB1 is not registered with the listener`, and it
  never recovers: the container then stays unhealthy (or, with a weaker
  check, "healthy" while serving HTML 404s).
- **The `data-api` healthcheck must require a successful response** (`curl
  -f`). Without `-f`, curl exits 0 for any HTTP status, compose reports
  "healthy" as soon as Tomcat answers with its HTML 404 page, and the ETL's
  first request fails before the webapp has deployed.
- **`db` has no persistent volume.** A teardown (`docker compose down`)
  discards the initialised database, so the next run reloads everything.
- **`db_webuser_permissions`** is a one-shot job that applies the SQL in
  `compose_files/sql/`; `cda-etl` is behind the `seed` profile so a plain `up`
  doesn't start it as a service.

## Fixtures

All in [`conftest.py`](conftest.py), session-scoped unless noted:

- **`cda_stack`** -- runs `docker compose up --wait` for `db` and `data-api`,
  then `docker compose --profile seed run --build --rm cda-etl`, yields the
  base URL and API key, and on teardown dumps container logs to
  `$CDA_COMPOSE_LOG` (if set) before `compose.stop()` removes the containers.
  Set `CDA_EXTERNAL_STACK_URL` to skip all of it and use a stack you started
  yourself (its mere presence enables the bypass); `CWMS_TEST_API_KEY` supplies
  that stack's key. Via Gradle use
  `-Ptestcontainer.cwms.bypass.url=...` and
  `-Ptestcontainer.cwms.bypass.apiKey=...` (re-read on every invocation,
  unlike environment variables an existing Gradle daemon may not see).
- **`cda_client`** -- a `requests` session with the API-key header.
- **`cwms_session`** -- points `cwms-python` at the stack once
  (`cwms.init_session()` keeps connection state at module level).
- **`regi_jvm`** -- starts the embedded JVM once per process. JPype cannot
  restart a JVM after it has been shut down, so every test shares one
  `regi_session()`; calculations still get their own `run_headless()` call.
- **`run_regi_calculation`** (function-scoped) -- runs `run_headless`, then
  **fails the test on any ERROR-level log record**. REGI's scriptable
  calculations catch and log most failures rather than raising them, so
  without this a calculation that did nothing returns normally.

Because these tests only run when explicitly selected with `-m integration`,
a missing prerequisite (Docker, the `regi_python` wheel, `cwms-python`) or a
stack that can't be brought up **fails** the session instead of skipping it.

Output series are seeded with history so the stack resembles production;
tests call `clear_timeseries` on their output window first so only data the
calculation wrote can satisfy the comparison.

## Seed data and the ETL

`cda-etl` reads [`regi.generated.yml`](compose_files/regi-data/regi.generated.yml).
The pipeline publishes office properties, then each project's data (locations,
projects, timeseries, clobs, ratings, outlets, turbines, locks, gate and
turbine changes, ...), then office location and timeseries groups -- groups
last, because they assign project locations that must already exist. An ETL
ref that publishes groups first fails with 404s on every group and aborts
before loading the projects. With `SOURCE_CDA_URL` set the ETL first stages
(downloads) the listed items into `compose_files/regi-data/`; without it, it
uses the staged files as they are.

`regi.generated.yml` is generated from
[`regi.yml`](compose_files/regi-data/regi.yml) plus
[`regi.templates.yml`](compose_files/regi-data/regi.templates.yml) by the
expander in [`../cda-etl-expander/`](../cda-etl-expander/) (the `cda-expander`
compose service; it needs `SOURCE_CDA_URL` to read association properties).
Without a source CDA, edit both files by hand with the same entry; the base
hash in the generated file's header is informational.

The `REGI-Test-Expected` version convention is described in Part 1; the seed
files for those series are ordinary files in `SWT/Timeseries/`.

## Running without Gradle

```
../gradlew :regi-headless:buildPythonWheel
pip install ../regi-headless/build/install/regi_python/dist/*.whl
pip install -r requirements.txt
pytest -m integration
```

When running `pytest` directly, `regi_python`'s embedded JVM uses whatever
`java` is on `PATH` unless `JAVA_HOME` points at a JDK new enough for the
compiled classes (the Gradle task requests that JDK through a toolchain in
[`build.gradle`](build.gradle)); otherwise
`regi_session()` fails with `UnsupportedClassVersionError` or `ImportError`.
The Gradle task sets this up through a JDK toolchain. Both `integrationTest`
and `regi-headless` use the `com.pswidersk.python-plugin` with `VenvTask`.

## Remote debugging the embedded JVM

[`regi_python.py`](../regi-headless/src/main/python/regi_python/regi_python.py)'s
`regi_session()` can start the JVM with a JDWP agent so IntelliJ (or any
JDWP-capable debugger) can attach and step through `:regi-headless` and its
compiled dependencies. Enable it in `gradle.properties` (see
[`../gradle.properties.template`](../gradle.properties.template)):

```
regiHeadless.debug.port=5005
regiHeadless.debug.suspend=y
```

then run `./gradlew :integration-tests:integrationTest`. `suspend=y` blocks
the JVM (and so the whole pytest session) at startup until a debugger
attaches; with the stack bypass in place that is the first thing that
happens, so there is no race. Use `suspend=n` to start immediately and pause
only at a breakpoint. In IntelliJ: **Run > Edit Configurations > + > Remote
JVM Debug**, host `localhost`, the same port, started before (or with
`suspend=n`, any time during) the run; make sure `:regi-headless` and any
attached sources are on that configuration's classpath so breakpoints
resolve. Leave both properties unset for normal runs: an open debug port with
`suspend=y` hangs any automated invocation waiting for a debugger.

## CI

[`../.github/workflows/integration-tests.yml`](../.github/workflows/integration-tests.yml)
runs `./gradlew :integration-tests:integrationTest` on demand and on pull
requests that touch this module, `regi-headless`, or the build files. The
compose stack and seeding are done by the `cda_stack` fixture, so the job only
frees disk space, sets up Java and Gradle, and runs the task. It sets
`CDA_COMPOSE_LOG` and `PYTEST_ADDOPTS` so the compose logs and a JUnit report
are uploaded as an artifact even when the run fails. Allow a generous
timeout: the database image start, the ETL load and the calculations all add
up.

## Things that have bitten before

- **A JVM that won't exit.** If pytest finishes its tests and then hangs,
  look for non-daemon threads left in the embedded JVM (`jcmd <pid>
  Thread.print`). `RowcpsExecutorHandler`'s monitor thread in `regi-tools`
  once ended only on an interrupt that could be lost and was not a daemon, so
  it kept the JVM alive; releases of `regi-tools` that make it a daemon and
  stop it on an explicit shutdown flag don't have the problem.
- **Stale installed wheel.** After changing `:regi-headless` or a dependency
  version, rebuild and reinstall the wheel (`buildPythonWheel`) or the JVM
  loads the old jars. The Gradle task reinstalls it for you.
- **Intermittent HTML 404s from `data-api`.** If a load fails with HTML error
  bodies instead of JSON, the CDA webapp wasn't up (or stopped routing);
  `docker compose restart data-api` clears it for a long-lived stack.
