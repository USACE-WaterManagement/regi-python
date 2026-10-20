# CDA integration tests

Docker-based integration tests that spin up a real CWMS database + CDA
(`cwms-data-api`) instance, seed it via `cda-etl`, and run tests against it --
as opposed to the JPype/reflection-based unit and smoke tests under
`regi-headless/src/test/python/`.

This is adapted from the `cwms-data-api` repo's own `docker-compose.yml`,
with two changes for automated testing from regi-python:

1. `data-api` runs from a pre-built image, and `cda-etl` is built from the
   CDA GitHub repo by compose.
2. Keycloak and the `traefik` HTTPS proxy are removed. Tests authenticate
   with a CWMS API key instead of an OpenID token.

`test_environment.py` covers infra-only: bringing the stack up healthy and
seeded. `test_inflow_calc.py`, `test_gate_flow_calc.py`, and
`test_gate_settings_calc.py` are the follow-up that exercises
`regi_python`/`run_headless` against the seeded data -- one calculation
family each, matching the three scriptable calculations `district-scripts/`
uses (Inflow, Gate Flow, Gate Settings). See "Calculation tests" below for
how they're structured, which one currently runs, and why the other two are
scaffolded but skipped.

## Prerequisites

1. **Docker**, with the `docker compose` CLI plugin, running locally.
2. **Images.** `data-api` pulls `ghcr.io/usace/cwms-data-api`, with the tag
   defaulting to `latest` and overridable via `CDA_DATA_API_VERSION`.
   `cda-etl` (and `cda-expander`) are built by Docker directly from
   `https://github.com/USACE/cwms-data-api.git` (subdir `cda-etl`) and tagged
   `cwms-data-api/etl:local` -- no published image is needed. Copy
   `.env.example` to `.env` to override `CDA_ETL_GIT_URL` / `CDA_ETL_GIT_REF`
   (set `develop` to track latest). The build needs network access to github.com and PyPI. 
    To build manually: `docker compose build cda-etl`.
3. **Config and seed data**, vendored in this repo under `compose_files/`:
   - `compose_files/sql/` (SQL grant script for the web user)
   - `compose_files/regi-data/` (the REGI ETL config -- `regi.yml`,
     `regi.templates.yml`, and the expander-generated `regi.generated.yml` --
     plus the seed data files under `SWT/` that it references)
4. Python deps: `pip install -r requirements.txt` -- includes `cwms-python`,
   which the calculation tests use to read/write CDA data (see "Calculation
   tests" below) instead of hand-rolled `requests` calls.
5. The `regi_python` wheel built by `:regi-headless`, installed into the same
   environment -- required so tests can eventually exercise `regi_python`
   against the seeded CDA data (see `test_environment.py`'s TODO).

## Running

Directly with a local `pytest` install (build and install the wheel first):

```
../gradlew :regi-headless:buildPythonWheel
pip install ../regi-headless/build/install/regi_python/dist/*.whl
pip install -r requirements.txt
pytest -m integration
```

Or via Gradle, using the same Gradle-managed Python venv approach
(`com.pswidersk.python-plugin` + `VenvTask`) as `regi-headless/build.gradle`:

```
./gradlew :integration-tests:integrationTest
```

The `cda_stack` fixture (in `conftest.py`) runs `docker compose up --wait`
for `db` and `data-api` (`db_webuser_permissions` runs first as a one-shot
job), then runs `cda-etl` once as a seeding step via
`docker compose --profile seed run --build --rm cda-etl` (it's gated behind the
`seed` profile so a plain `up` doesn't try to start it as a long-running
service). The stack is torn down at the end of the session.

Tests are skipped, with an explanatory message, if Docker isn't available or
the stack can't be brought up.

If you've already brought the stack up yourself (`docker compose up --wait
db data-api && docker compose --profile seed run --rm cda-etl`), the
`cda_stack` fixture can skip managing docker compose altogether -- no
`compose.start()`/`compose.stop()`, no reseed -- and just point tests at
what's already running. This avoids both the compose bring-up wait and the
forced Oracle reinit that `compose.stop()` otherwise causes on every session
teardown (see the `db` note below).

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

`regi_python`'s `regi_session()` can start the embedded JVM with a JDWP agent
so IntelliJ (or any JDWP-capable debugger) can attach to it and step through
`:regi-headless` and any of its compiled dependencies (e.g. the
`mil.army.usace.hec.serversuite.cda.*` classes involved in the login issue
below).

Enable it via `gradle.properties` (same mechanism as the CDA bypass
properties above) -- uncomment/add:

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

`test_inflow_calc.py`, `test_gate_flow_calc.py`, and `test_gate_settings_calc.py`
all follow the same shape:

1. Run a real calculation (through `regi_python`'s `run_headless`, via the
   session-scoped `run_regi_calculation` fixture in `conftest.py`) against
   data seeded by `regi.yml`.
2. Fetch the timeseries the calculation just wrote from CDA, via
   `regi_calc_support.fetch_timeseries` -- a thin wrapper around
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

There's no separate structure in `regi.yml` for "the expected answer" --
instead, a reference series is seeded as a perfectly ordinary timeseries
entry under the same location/parameter the calculation writes to, but
tagged with the version token `REGI-Test-Expected` instead of a real REGI/CWMS
version (e.g. `EUFA.Flow-Res In.Ave.~1Day.1Day.REGI-Test-Expected`, next to the
`Regi-Rev-Adjusted` version the Inflow calculation actually writes). Nothing
ever computes into a `REGI-Test-Expected` series; it exists purely as this test
suite's frozen comparison target, and its seed file under
`compose_files/regi-data/SWT/Timeseries/` is a plain data file like any
other.

For `test_inflow_calc.py`, that reference was created by freezing a few days
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
   `compose_files/regi-data/SWT/Properties/`).
2. Pick a comparison window fully inside the seeded period of record,
   away from either edge.
3. Copy that ts id's currently-seeded values for the window into a new
   `...REGI-Test-Expected` seed file (same shape, different `name`/version).
4. Add the new id to the project's `timeseries:` list in `regi.yml`.
5. Write the test: run the calculation, fetch both series, compare.

If no seeded historical output already exists for what you're testing,
running the calculation once against real/trusted data and manually
verifying its output is correct -- then freezing *that* as the
`REGI-Test-Expected` reference -- works the same way.

### Current coverage

- **Inflow** (`test_inflow_calc.py`): fully implemented and passing
  end-to-end against a live seeded stack. `cwms.get_timeseries()`'s default
  unit system (`unit="EN"`) is assumed to already match the seeded data's
  units (`cfs`) with no conversion, and `autoAdjust`'s behavior at the edges
  of its input period of record is unconfirmed. Its `REGI-Test-Expected`
  reference (`EUFA.Flow-Res In.Ave.~1Day.1Day.REGI-Test-Expected`) has a seed
  file under `compose_files/regi-data/SWT/Timeseries/`, but was missing from
  `regi.yml`'s (and `regi.generated.yml`'s) EUFA `timeseries:` list, so
  `cda-etl` never loaded it -- that 404 on the expected series is what made
  the test fail. Fixed by adding it to both files.
- **Gate Flow** (`test_gate_flow_calc.py`): five cases pass end-to-end, one
  is skipped. Each case runs `computeFlowGroup` for a flow group and compares
  the series it writes against a frozen `REGI-Test-Expected` series (see
  "Known-good reference series" above). `FLOW_GROUPS` entries default to EUFA
  and the June 1 -> June 3..7 window; other projects override `project_id`
  and, where needed, the window.

  | Case | Output ts compared | Notes |
  |---|---|---|
  | `Project_Total` (EUFA) | `Flow-Res Out.Ave.~1Day.1Day` | real seeded history |
  | `Gated_Total` (EUFA) | `Flow-Controlled.Ave.1Hour.1Hour` | window is all zero (gates closed that week) |
  | `Turbine_Total` (EUFA) | `Flow-Power.Ave.1Hour.1Hour` | real seeded history |
  | `FCOB_Uncontrolled_Total` | `FCOB.Flow-Uncontrolled.Ave.1Hour.1Hour` | **synthetic elevations**, see below |
  | `KEYS_TainterGate_Total` | `KEYS.Flow-RES-TGs.Ave.1Hour.1Hour.regi` | window 06-25..06-29, after KEYS' first gate change; the CLOB's output version is `regi`, not `Rev-Regi-Flowgroup` |
  | `Uncontrolled_Total` (EUFA) | -- | skipped: its CLOB has an empty `<time_series_set/>` and EUFA has no uncontrolled-spillway rating |

  *FCOB uses synthetic data.* FCOB's real 2026 pool tops out near 1342.3 ft,
  about 12.5 ft below the uncontrolled-spillway crest (1354.8 ft in
  `FCOB.Elev;Flow-Uncontrolled_Spillway`), and 2025 has no data on the test
  CDA, so a real window would only ever produce zeros.
  `FCOB.Elev.Inst.1Hour.0.Ccp-Rev` is therefore edited for 2026-06-04..06-06
  to hold 1355.0 / 1356.0 / 1356.5 ft for one day each (exact points on the
  2013 rating, which is the effective curve; the spec's in-range method is
  `PREVIOUS`, so exact points avoid any interpolation question). The expected
  series is computed from those elevations and the rating, not from REGI's
  output: 23.2450894 / 341.631648 / 576.049241 cfs on the plateaus, and each
  hour is the mean of the flows at its start and end, so the day-boundary
  hours are halfway (e.g. 11.6225447 at 06-04 00:00). REGI reproduces every
  value.

  *Why these tests can fail.* REGI catches and logs most calculation
  failures (e.g. "Unable to compute flow group ...") instead of raising, and
  the output series are seeded with history, so an earlier version of these
  tests passed even though every calculation was failing. Two guards now
  prevent that: `run_regi_calculation` (in `conftest.py`) fails the test on
  any ERROR-level log record emitted during the run, and each Gate Flow case
  calls `clear_timeseries` on its output window first so only data the
  calculation wrote can satisfy the comparison. Other tests that use
  `run_regi_calculation` get the error check too.

  *Not covered.* The other EUFA groups (`Controlled`, `EUFA Turbine_Total`,
  `Lock_Total`, `Pump_*_Total`) have an empty `<time_series_set/>` in their
  CLOBs, so `computeFlowGroup` has nothing to write; `SluiceGate_Total` and
  `TainterGate_Total` have output config but no seeded data and no gate-change
  history that would make them non-zero. KEYS/WEBB/FCOB `Project_Total`,
  `Gated_Total` and `Turbine_Total`, FCOB `Pump_Out_Total`, and `computeAll`
  and the multi-location overloads are untested.

- **Gate Settings** (`test_gate_settings_calc.py`): `SG1` and `TG1` pass
  end-to-end. `createGateSettingsOutlet` does not write a timeseries; it
  persists CWMS gate-change records, which the test reads back from CDA for
  the 2026-07-17..07-22 window. Getting there took four fixes (Rating-category
  location groups in `regi.yml`, the bare sub-location outlet id, the window,
  and per-outlet opening timeseries), plus the `regi-tools` 10.0.0 bump for
  the `retrieveRatingGroups()` 409 on commit -- the module docstring has the
  traces. Frozen values come from the seeded input timeseries and match what
  REGI wrote: SG1 opens 0.5 ft at 07-17 00:00Z and 1.2 ft at 07-19 00:00Z;
  TG1 opens 1.0 ft and 3.5 ft at the same times. The gate-changes in the
  window are deleted before and after each test (EUFA's seeded changes are all
  outside the window), so what's asserted was written by the calculation.
  Known gap: the inputs also close each gate at 07-21 12:00Z, and REGI logs
  that as a modification but stores no gate change for it; the test
  documents this and fails if that behavior changes. `cwms.get_all_gate_changes`
  and `delete_gate_change` send an `Accept` header CDA rejects with a 406, so
  the test calls `cwms.api` with `api_version=1` instead.

## Notes / things verified against the real images

- The API-key header format in `conftest.py`'s `cda_client` fixture
  (`Authorization: apikey <key>`) is confirmed correct against a real running
  `ghcr.io/usace/cwms-data-api` instance -- both `cda_client`'s raw REST calls
  and `cwms_session`'s `cwms.init_session(api_key=...)` work as documented.
- The `regi_jvm` login issue previously documented here (`ServerSuiteUtil.login`
  getting back `401 {"message":"No credentials provided."}`) is resolved --
  `run_regi_calculation` now logs in and runs real calculations end-to-end
  against a live seeded stack (confirmed via `test_inflow_calc.py` and
  `test_gate_flow_calc.py`).
- **Resolved**: `run_regi_calculation` used to leave the pytest process
  hanging indefinitely during JVM teardown after all assertions had already
  passed. A thread dump showed no calculation thread active -- the JVM was
  idle except for an "Active Reference Queue Daemon" thread spinning in a
  tight loop (`rma.util.lookup.implspi.ActiveQueue$Impl.remove`),
  continuously constructing and discarding `InterruptedException`s. The
  `update to netbeans lookup` commit that moved `:regi-headless`'s own
  `@ServiceProvider` classes from `rma.services.annotations` to
  `org.openide.util.lookup` didn't fix this: `mil.army.usace.hec:lookup:2.0`
  (the old standalone `rma.util.lookup` implementation, containing the buggy
  `ActiveQueue$Impl`) is still pulled in transitively via
  `hec-nucleus-*`/`cwms-db-dao`, sits on the classpath alongside
  `mil.army.usace.hec:lookup-compat:4.0.0` (a newer shim that delegates the
  same `rma.util.lookup.Lookup`/`Lookups` API to `org.openide.util.lookup`
  instead), and -- because of classpath-wildcard jar ordering -- kept winning
  the race for the `rma.util.lookup.Lookup` class. Any HEC code still calling
  into `rma.util.lookup.*` (e.g. `ServerSuiteUtil.login`) got the buggy
  implementation regardless of what `:regi-headless`'s own code used.
  Fixed by excluding `mil.army.usace.hec:lookup` in
  `regi-headless/build.gradle`'s `configurations.configureEach` block, so
  `lookup-compat` is the only remaining provider of that class. Verified via
  an isolated JVM repro (the spinning thread is gone, `rma.util.lookup.Lookup`
  now resolves from `lookup-compat-4.0.0.jar`) and end-to-end: `test_inflow_calc.py`
  now passes and exits immediately (no teardown hang), where before this exact
  scenario was documented to hang. One caught, non-fatal side effect: without
  the old jar, `ServerSuiteUtil.login`'s call into `rma.util.lookup.Lookups.forPath`
  now falls through to `org.openide.util`'s `NamedServicesProvider`, which logs a
  caught `NoClassDefFoundError` (`org/netbeans/core/startup/Main` -- expected,
  since `org.netbeans.modules` is deliberately excluded from this project) as a
  WARNING; login still succeeds.
- `db`'s healthcheck has a 40-minute `start_period` (matches the upstream CDA
  compose file) because first-time Oracle initialization is slow; the first
  run in a fresh environment will be slow. Subsequent `docker compose up`s
  reuse the same "database-ready" image layer and come up in seconds --
  **but a `docker compose down` (or a testcontainers-driven teardown, which
  defaults to this) throws that baked-in state away**, since `db` has no
  persistent volume; expect a full ETL reseed after any teardown.
- When running directly with `pytest` (bypassing the `integrationTest` Gradle
  task), `regi_python`'s embedded JVM picks up whatever `java` is on `PATH`
  unless `JAVA_HOME` points at a JDK new enough for the compiled classes
  (JDK 21 as of this writing) -- otherwise `regi_session()` fails with
  `UnsupportedClassVersionError`/`ImportError` before running anything. The
  Gradle task sets this up via a JDK toolchain automatically; a direct
  `pytest` invocation needs `JAVA_HOME` set by hand.
- `data-api` has intermittently stopped routing requests correctly (`GET`s to
  real endpoints return the SPA's `index.html` with a 404 status) after
  running for a while, with no corresponding error in its own logs; a plain
  `docker compose restart data-api` has reliably cleared it when seen during
  this work. Not something this repo's config controls -- worth watching for
  if a seed run fails with HTML error bodies instead of JSON ones.
