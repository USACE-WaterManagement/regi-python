# CDA integration tests

Docker-based integration tests that spin up a real CWMS database + CDA
(`cwms-data-api`) instance, seed it via `cda-etl`, and run tests against it --
as opposed to the JPype/reflection-based unit and smoke tests under
`regi-headless/src/test/python/`.

This is adapted from the `cwms-data-api` repo's own `docker-compose.yml`,
with two changes for automated testing from regi-python:

1. `data-api` and `cda-etl` run from pre-built images instead of being built
   from a checked-out CDA source tree.
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
2. **Real image references.** `data-api` pulls `ghcr.io/usace/cwms-data-api`,
   with the tag defaulting to `latest` and overridable via
   `CDA_DATA_API_VERSION`. Copy `.env.example` to `.env` and fill in
   `CDA_ETL_IMAGE` with an actual, pre-built image tag for `cda-etl` --
   that placeholder in `docker-compose.yml` will not pull as-is.
3. **CDA-owned config and sample data**, copied from a `cwms-data-api`
   checkout (not vendored in this repo -- see the README in each spot):
   - `compose_files/` (SQL grant script, TLS certs, Togglz/Tomcat config,
     entrypoint scripts)
   - `cda-etl/data/sample-data/` (the `sample-app.yml` ETL config and the
     sample data files it references)
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
for `db`, `db_webuser_permissions`, `minio`, `minio-setup`, and `data-api`,
then runs `cda-etl` once as a seeding step via
`docker compose --profile seed run --rm cda-etl` (it's gated behind the
`seed` profile so a plain `up` doesn't try to start it as a long-running
service). The stack is torn down at the end of the session.

Tests are skipped, with an explanatory message, if the required assets or
real image env vars above aren't in place -- so `pytest` won't hang trying
to pull placeholder images.

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

- **Inflow** (`test_inflow_calc.py`): fully implemented, following the
  pattern above. `cwms.get_timeseries()`'s default unit system (`unit="EN"`)
  is assumed to already match the seeded data's units (`cfs`) with no
  conversion, and `autoAdjust`'s behavior at the edges of its input period of
  record is unconfirmed. Blocked from actually running end-to-end by the
  `regi_jvm` login issue below.
- **Gate Flow** (`test_gate_flow_calc.py`): fully implemented. EUFA now has
  real outlets/turbines/gate-changes and a `Flow.EUFA.Project_Total` location
  group seeded, and `computeFlowGroup`'s real output ts id was confirmed
  against a live seeded stack: `EUFA.Flow-Res Out.Ave.~1Day.1Day.Rev-Regi-Flowgroup`
  (parameter "Flow-Res Out", version "Rev-Regi-Flowgroup" -- the flow-group
  analog of Inflow's "Regi-Rev-Adjusted"). The `REGI-Test-Expected` reference
  was frozen from that series' own already-seeded values. Also blocked from
  running end-to-end by the `regi_jvm` login issue below.
- **Gate Settings** (`test_gate_settings_calc.py`): scaffolded but still
  `pytest.mark.skip`'d, with a corrected design. Source inspection of
  `ScriptableGateSettingsImpl` (in :regi-headless) shows `createGateSettingsOutlet`
  does *not* write a plain timeseries at all -- it persists real CWMS
  gate-change records (fetchable via `cwms.get_all_gate_changes`), not an
  "Opening"-parameter ts. The test now targets that shape and is parametrized
  over `EUFA-SG1`/`EUFA-TG1` (both now real seeded outlets). It stays skipped
  because `EUFA.Opening.Inst.0.0.MANUAL` (the calc's input) has no seeded
  point data, and EUFA's only seeded gate-change history (mid/late July 2026)
  doesn't overlap the June 2026 window every other test here uses -- see the
  test's module docstring for exactly what's needed to unskip it.

## Notes / things verified (and one still-open issue) against the real images

- The API-key header format in `conftest.py`'s `cda_client` fixture
  (`Authorization: apikey <key>`) is confirmed correct against a real running
  `ghcr.io/usace/cwms-data-api` instance -- both `cda_client`'s raw REST calls
  and `cwms_session`'s `cwms.init_session(api_key=...)` work as documented.
- **Open issue**: `regi_jvm`/`run_regi_calculation` (i.e. any real
  `run_headless()` call) currently fails before running any calculation.
  `HeadlessRegiDomainFactory.createDomain()`'s login (`ServerSuiteUtil.login`
  -> `GET /cwms-data/user/profile`) gets back `401 {"message":"No credentials
  provided."}` even though the exact same `CDA_API_KEY` value works for every
  other call path (cda-etl, cwms-python, raw `curl` with the `apikey` header).
  This points at the compiled `mil.army.usace.hec.serversuite.cda.*` client
  classes not attaching the key for that specific request, not at the seeded
  data or this repo's own config -- needs someone with visibility into that
  library (or a newer/older version of it) to chase further. Until it's
  fixed, none of the calculation tests here can actually execute past
  `run_regi_calculation`, even though their CDA-side setup (seed data,
  fixtures, comparison logic) is confirmed correct independently.
- `db`'s healthcheck has a 40-minute `start_period` (matches the upstream CDA
  compose file) because first-time Oracle initialization is slow; the first
  run in a fresh environment will be slow. Subsequent `docker compose up`s
  reuse the same "database-ready" image layer and come up in seconds --
  **but a `docker compose down` (or a testcontainers-driven teardown, which
  defaults to this) throws that baked-in state away**, since `db` has no
  persistent volume; expect a full ETL reseed after any teardown.
- `data-api` has intermittently stopped routing requests correctly (`GET`s to
  real endpoints return the SPA's `index.html` with a 404 status) after
  running for a while, with no corresponding error in its own logs; a plain
  `docker compose restart data-api` has reliably cleared it when seen during
  this work. Not something this repo's config controls -- worth watching for
  if a seed run fails with HTML error bodies instead of JSON ones.
