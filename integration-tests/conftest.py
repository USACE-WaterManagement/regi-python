"""
Session-scoped fixtures that bring up the CDA + CWMS database docker stack
(see docker-compose.yml) and seed it via cda-etl, so integration tests have a
real CDA instance with known data to talk to.

Requires:
  - Docker (with the `docker compose` CLI plugin) available on PATH.
  - compose_files/ (SQL grants and the REGI ETL config/seed data under
    compose_files/regi-data/), vendored in this repo.
  - Network access to GitHub, to build the cda-etl image (see README.md).
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest
import requests
from testcontainers.compose import DockerCompose

INTEGRATION_TESTS_ROOT = Path(__file__).resolve().parent
CDA_TEST_API_KEY = os.environ.get("CWMS_TEST_API_KEY", "ak1_SZUNxN3nDx0NpUfOJxpOuGqbqRKdYjbx86x6YVISLb9DiBi3Io5o6T6UFvkHknjIRnRO6oQfA1q6rP4XRDYMH9Hlr4ndffL6NjxPUaBZLSnqukV0uGuZKOUWBB04L5SyloJniOHkFe6ymvB9tzeziGYwzrDv3k6lzacG9vftHkCHB1QbjwwCC0sDkFvuwCe9qnyx5us11qL0YAfKXhe0fBCA2TmNDz8WXfw1HfBnAKx6WD7KqHngplWu4miOvkNverxFmAdJ")
CDA_PORT = int(os.environ.get("CDA_PORT", "7000"))
CDA_BASE_URL = f"http://localhost:{CDA_PORT}/cwms-data/"

CDA_EXTERNAL_STACK_URL = os.environ.get("CDA_EXTERNAL_STACK_URL")


def _require_docker():
    """
    Fails the session, with an explanatory message, if Docker/`docker compose`
    aren't usable. These tests only run when explicitly selected
    (`-m integration`), so a missing prerequisite is an error, not a skip.
    """
    if shutil.which("docker") is None:
        pytest.fail("Docker is not installed/on PATH -- see README.md prerequisites.", pytrace=False)

    try:
        subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True, text=True, check=True, timeout=10,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        pytest.fail("The `docker compose` CLI plugin is not available -- see README.md prerequisites.", pytrace=False)

    try:
        subprocess.run(
            ["docker", "info"],
            capture_output=True, text=True, check=True, timeout=10,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        pytest.fail("Docker daemon is not running/reachable -- see README.md prerequisites.", pytrace=False)


@pytest.fixture(scope="session")
def cda_stack():
    """
    Starts db and data-api (via docker compose), waits for them to
    report healthy, then runs cda-etl once as a seeding step. Yields
    connection info for the running data-api.

    Set CDA_EXTERNAL_STACK_URL (e.g. http://localhost:7000/cwms-data/) to skip
    all of that and just point tests at a stack you brought up (and seeded)
    yourself -- e.g. via `docker compose up --wait db data-api && docker
    compose --profile seed run --rm cda-etl` -- so `compose.stop()` doesn't
    tear it down (and force a full Oracle reinit, see README.md) at the end
    of every test session.
    """
    if CDA_EXTERNAL_STACK_URL:
        yield {"base_url": CDA_EXTERNAL_STACK_URL, "api_key": CDA_TEST_API_KEY}
        return

    _require_docker()

    # No `pull=True`: `data-api` pulls a real tag, but `cda-etl`/`cda-expander`
    # are built from the cwms-data-api git repo (see README.md prerequisite
    # #2) and tagged locally, so there is no registry to pull them from. The
    # build itself happens in `_seed_via_cda_etl` (`run --build`).
    #
    # `services=["db", "data-api"]` restricts what `--wait` waits *on* --
    # `db_webuser_permissions` and `cda-expander` still run first as their
    # declared dependencies, but as one-shot jobs (`restart: "no"`) they exit
    # after doing their job, which `--wait` otherwise (wrongly) treats as a
    # failure and reports exit code 1 even though the exit was 0 and
    # everything came up fine.
    compose = DockerCompose(
        context=str(INTEGRATION_TESTS_ROOT),
        compose_file_name="docker-compose.yml",
        wait=True,
        services=["db", "data-api"],
    )
    try:
        compose.start()
    except Exception as exc:
        # testcontainers keeps compose's own output on the exception; without
        # it the reason (unhealthy service, pull failure, ...) is lost.
        output = "".join(
            f"\n--- {name} ---\n" + value.decode(errors="ignore")[-4000:]
            for name in ("stdout", "stderr")
            if isinstance(value := getattr(exc, name, None), bytes) and value
        )
        _dump_compose_logs()
        raise RuntimeError(
            f"Could not bring up the CDA docker stack (see README.md prerequisites): {exc}{output}"
        ) from exc

    try:
        # Not caught above: a seeding failure here means the stack came up
        # fine but cda-etl itself failed (e.g. a real bug in regi.yml/seed
        # data), which should fail the test session, not skip it silently.
        _seed_via_cda_etl(compose)
        yield {"base_url": CDA_BASE_URL, "api_key": CDA_TEST_API_KEY}
    finally:
        # Must run before compose.stop(), which removes the containers and
        # their logs.
        _dump_compose_logs()
        compose.stop()


def _dump_compose_logs():
    """
    Writes every compose service's logs to $CDA_COMPOSE_LOG when that env var
    is set (CI sets it so a failed run leaves the db/data-api logs behind).
    Never raises: diagnostics must not mask the real test result.
    """
    log_path = os.environ.get("CDA_COMPOSE_LOG")
    if not log_path:
        return
    try:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["docker", "compose", "--profile", "seed", "logs", "--no-color", "--timestamps"],
            cwd=INTEGRATION_TESTS_ROOT, capture_output=True, text=True, timeout=120,
        )
        Path(log_path).write_text(result.stdout + result.stderr, encoding="utf-8")
    except Exception as exc:
        print(f"Could not collect docker compose logs: {exc}")


def _seed_via_cda_etl(compose: DockerCompose):
    """Runs the cda-etl one-shot job (gated behind the `seed` compose profile)."""
    seed_compose = DockerCompose(
        context=str(INTEGRATION_TESTS_ROOT),
        compose_file_name="docker-compose.yml",
        profiles=["seed"],
    )
    cmd = seed_compose.docker_compose_command() + ["run", "--build", "--rm", "cda-etl"]
    result = subprocess.run(
        cmd, cwd=INTEGRATION_TESTS_ROOT, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            "cda-etl seeding failed "
            f"(exit {result.returncode}):\nstdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


@pytest.fixture(scope="session")
def cda_client(cda_stack):
    """A `requests.Session` pre-configured with the test CDA API key."""
    session = requests.Session()
    session.headers.update({"Authorization": f"apikey {cda_stack['api_key']}"})
    return session


@pytest.fixture(scope="session")
def cwms_session(cda_stack):
    """
    Points cwms-python at the seeded stack once for the whole test session.

    `cwms.init_session()` sets module-level state inside the `cwms` package
    (a shared `requests` session with the base URL and auth header baked
    in) rather than returning an object callers thread through every call,
    so calling it once here -- before any test calls `cwms.get_timeseries`
    et al. -- is enough for the whole session. Depend on this fixture (even
    if only for its side effect) in any test that reads/writes CDA data
    through cwms-python.
    """
    try:
        import cwms
    except ImportError:
        pytest.fail("cwms-python is not installed -- pip install -r requirements.txt.", pytrace=False)

    cwms.init_session(api_root=cda_stack["base_url"], api_key=cda_stack["api_key"])


@pytest.fixture(scope="session")
def regi_jvm(cda_stack):
    """
    Starts the regi_python JVM once for the whole test session and points it
    at the seeded stack.

    Session-scoped deliberately: `regi_python.regi_session()` cannot be
    entered a second time after its JVM has been shut down in this process
    (JPype does not support restarting a JVM), so every test that runs a
    calculation must share one `regi_session()` rather than each opening and
    closing its own. Individual calculations still run through their own
    `run_headless()` call (see the `run_regi_calculation` fixture below) --
    only the JVM itself is shared.

    Requires the `regi_python` wheel built by :regi-headless to be installed
    (see README.md); fails with an explanatory message if it isn't.
    """
    try:
        import regi_python  # noqa: F401
    except ImportError:
        pytest.fail(
            "regi_python is not installed -- build/install the wheel first "
            "(see README.md), or run via `./gradlew :integration-tests:integrationTest`.",
            pytrace=False,
        )

    os.environ["CDA_URL"] = cda_stack["base_url"]
    os.environ["CDA_API_KEY"] = cda_stack["api_key"]
    os.environ.setdefault("OFFICE_ID", "SWT")

    from regi_python import regi_session

    with regi_session():
        yield


@pytest.fixture
def run_regi_calculation(regi_jvm, caplog):
    """
    Returns a function that runs `run_headless` (from regi_python) with a
    `callback(registry)` for the current test. Depending on `regi_jvm` (not
    calling regi_session() itself) is what makes JVM startup/shutdown happen
    once per session instead of once per test.

    REGI's scriptable calculations catch and *log* most failures (for
    example "Unable to compute flow group ...") instead of raising them, so
    a calculation that did nothing returns normally. Any ERROR-level log
    record emitted during the run therefore fails the test, otherwise a
    comparison against already-seeded output could pass without the
    calculation ever having written anything.
    """
    import logging

    from regi_python import run_headless

    def run(callback):
        caplog.clear()
        with caplog.at_level(logging.ERROR):
            run_headless(callback)
        errors = [
            f"{record.name}: {record.getMessage()}"
            for record in caplog.records
            if record.levelno >= logging.ERROR
        ]
        assert not errors, "REGI logged error(s) during the calculation:\n" + "\n".join(errors)

    return run
