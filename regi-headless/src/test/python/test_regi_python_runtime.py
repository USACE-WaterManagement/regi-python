"""
Runtime state checks for regi_python.regi_python.

Covers:
  * run_headless happy path: callback runs, commit happens, executor
    shutdown + domain closing happen, in the right order.
  * run_headless exception path: callback raises, commit is skipped,
    executor shutdown + domain closing still happen, exception propagates.
  * run_headless commit-failure path: commitData itself raises, executor
    shutdown + domain closing still happen, exception propagates.
  * run_headless executor timeout: awaitTermination(False) escalates to
    shutdownNow().
  * regi_session does not start or shut down a JVM that was already
    running before it was entered (it only tears down what it started).
  * regi_session JVM lifecycle: JVM gets started, JUL->Python logging gets
    configured, JVM gets shut down on exit -- in that order.
  * regi_session propagates an exception raised inside the `with` block
    while still shutting down the JVM it started.
  * regi_session surfaces a clear, chained error if the JVM fails to
    restart in the same process.
  * _prepend_java_home_to_path() is a no-op without JAVA_HOME, prepends
    JAVA_HOME/bin onto PATH when it's missing, and doesn't duplicate it
    when it's already present.
"""

import os
import types

import pytest


class FakeExecutorService:
    """Stand-in for usace.rowcps.regi.factories.RowcpsExecutorService."""

    instances = {}

    def __init__(self, manager_id, calls, await_result=True):
        self.manager_id = manager_id
        self._calls = calls
        self._await_result = await_result

    def shutdown(self):
        self._calls.append(("executor.shutdown", self.manager_id))

    def awaitTermination(self, timeout, unit):
        self._calls.append(("executor.awaitTermination", timeout))
        return self._await_result

    def shutdownNow(self):
        self._calls.append(("executor.shutdownNow", self.manager_id))

    @classmethod
    def getInstance(cls, manager_id):
        return cls.instances[manager_id]


class FakeRegiDomain:
    def __init__(self, calls, commit_error=None):
        self._calls = calls
        self._commit_error = commit_error

    def commitData(self, manager_id):
        self._calls.append(("domain.commitData", manager_id))
        if self._commit_error is not None:
            raise self._commit_error

    def closing(self):
        self._calls.append(("domain.closing",))


class FakeHeadlessRegiDomainFactory:
    def __init__(self, domain, manager_id):
        self._domain = domain
        self._manager_id = manager_id

    def createDomain(self):
        return self._domain

    def getManagerId(self):
        return self._manager_id


def _install_fake_java_modules(
    monkeypatch, calls, manager_id="mgr-1", await_result=True, commit_error=None
):
    """Patch sys.modules so run_headless's inline Java imports resolve to fakes."""
    import sys

    domain = FakeRegiDomain(calls, commit_error=commit_error)
    factory = FakeHeadlessRegiDomainFactory(domain, manager_id)
    executor = FakeExecutorService(manager_id, calls, await_result=await_result)
    FakeExecutorService.instances[manager_id] = executor

    headless_module = types.ModuleType("usace.rowcps.headless")
    headless_module.HeadlessRegiDomainFactory = lambda: factory
    headless_module.RegiCalcRegistry = lambda regi_domain, mgr_id: ("registry", regi_domain, mgr_id)

    factories_module = types.ModuleType("usace.rowcps.regi.factories")
    factories_module.RowcpsExecutorService = FakeExecutorService

    concurrent_module = types.ModuleType("java.util.concurrent")
    concurrent_module.TimeUnit = types.SimpleNamespace(MILLISECONDS="MILLISECONDS")

    monkeypatch.setitem(sys.modules, "usace.rowcps.headless", headless_module)
    monkeypatch.setitem(sys.modules, "usace.rowcps.regi.factories", factories_module)
    monkeypatch.setitem(sys.modules, "java.util.concurrent", concurrent_module)

    return domain, executor


@pytest.fixture
def cda_env(monkeypatch):
    monkeypatch.setenv("CDA_URL", "https://example.test")
    monkeypatch.setenv("CDA_API_KEY", "test-key")
    monkeypatch.setenv("OFFICE_ID", "TEST")


def test_run_headless_invokes_callback_commits_and_closes(monkeypatch, cda_env):
    """Happy path: callback runs, commit occurs, shutdown occurs, closing occurs."""
    import regi_python.regi_python as bridge

    calls = []
    domain, executor = _install_fake_java_modules(monkeypatch, calls)

    callback_calls = []

    def callback(registry):
        callback_calls.append(registry)
        calls.append(("callback", registry))

    bridge.run_headless(callback)

    assert len(callback_calls) == 1
    assert callback_calls[0] == ("registry", domain, "mgr-1")

    # Order matters: callback -> commit -> executor shutdown -> domain closing.
    assert calls == [
        ("callback", ("registry", domain, "mgr-1")),
        ("domain.commitData", "mgr-1"),
        ("executor.shutdown", "mgr-1"),
        ("executor.awaitTermination", 3000),
        ("domain.closing",),
    ]


def test_run_headless_exception_skips_commit_but_still_shuts_down_and_closes(monkeypatch, cda_env):
    """Callback raises: commit must not run, shutdown/closing must still run, error propagates."""
    import regi_python.regi_python as bridge

    calls = []
    domain, executor = _install_fake_java_modules(monkeypatch, calls)

    logged_errors = []
    monkeypatch.setattr(
        bridge.logger,
        "error",
        lambda msg, *args, **kwargs: logged_errors.append((msg, kwargs)),
    )

    boom = ValueError("callback exploded")

    def callback(registry):
        calls.append(("callback", registry))
        raise boom

    with pytest.raises(ValueError) as excinfo:
        bridge.run_headless(callback)

    assert excinfo.value is boom

    # No commit should have happened.
    assert ("domain.commitData", "mgr-1") not in calls

    # Cleanup must still have run.
    assert ("executor.shutdown", "mgr-1") in calls
    assert ("executor.awaitTermination", 3000) in calls
    assert ("domain.closing",) in calls

    # Cleanup happens after the callback and in the finally block, i.e. last.
    assert calls[-1] == ("domain.closing",)

    # Failure should have been logged with exc_info for traceback capture.
    assert logged_errors
    assert logged_errors[0][1].get("exc_info") is True


def test_run_headless_escalates_to_shutdown_now_on_termination_timeout(monkeypatch, cda_env):
    """If graceful executor termination times out, shutdownNow() must be called."""
    import regi_python.regi_python as bridge

    calls = []
    _install_fake_java_modules(monkeypatch, calls, manager_id="mgr-timeout", await_result=False)

    bridge.run_headless(lambda registry: None)

    assert ("executor.shutdown", "mgr-timeout") in calls
    assert ("executor.shutdownNow", "mgr-timeout") in calls


def test_run_headless_shuts_down_and_closes_even_when_commit_raises(monkeypatch, cda_env):
    """If commitData itself raises, executor shutdown + domain closing must still run, and the error propagates."""
    import regi_python.regi_python as bridge

    calls = []
    commit_error = RuntimeError("commit failed")
    domain, executor = _install_fake_java_modules(
        monkeypatch, calls, manager_id="mgr-commit-fail", commit_error=commit_error
    )

    logged_errors = []
    monkeypatch.setattr(
        bridge.logger,
        "error",
        lambda msg, *args, **kwargs: logged_errors.append((msg, kwargs)),
    )

    callback_calls = []

    def callback(registry):
        callback_calls.append(registry)
        calls.append(("callback", registry))

    with pytest.raises(RuntimeError) as excinfo:
        bridge.run_headless(callback)

    assert excinfo.value is commit_error

    # The callback did run, and commitData was attempted (that's what raised).
    assert len(callback_calls) == 1
    assert ("domain.commitData", "mgr-commit-fail") in calls

    # Cleanup must still have run despite the commit failure.
    assert ("executor.shutdown", "mgr-commit-fail") in calls
    assert ("executor.awaitTermination", 3000) in calls
    assert ("domain.closing",) in calls
    assert calls[-1] == ("domain.closing",)

    # Failure should have been logged with exc_info for traceback capture.
    assert logged_errors
    assert logged_errors[0][1].get("exc_info") is True


def test_regi_session_only_shuts_down_jvm_it_started(monkeypatch):
    """If a JVM is already running on entry, regi_session must not start or stop it."""
    import regi_python.regi_python as bridge

    started = []
    stopped = []
    jul_configured = []

    monkeypatch.setattr(bridge.jpype, "isJVMStarted", lambda: True)
    monkeypatch.setattr(bridge.jpype, "startJVM", lambda *args, **kwargs: started.append((args, kwargs)))
    monkeypatch.setattr(bridge.jpype, "shutdownJVM", lambda: stopped.append(True))
    monkeypatch.setattr(bridge, "configure_jul_to_python_logging", lambda logger: jul_configured.append(logger))

    with bridge.regi_session():
        pass

    assert started == []
    assert stopped == []
    assert jul_configured == []


def test_regi_session_starts_configures_logging_and_shuts_down(monkeypatch):
    """JVM state transitions through regi_session: started -> logger configured -> shut down."""
    import regi_python.regi_python as bridge

    jvm_state = {"started": False}
    calls = []

    def fake_is_jvm_started():
        return jvm_state["started"]

    def fake_start_jvm(*args, **kwargs):
        calls.append(("startJVM", args, kwargs))
        jvm_state["started"] = True

    def fake_shutdown_jvm():
        calls.append(("shutdownJVM",))
        jvm_state["started"] = False

    def fake_configure_jul(python_logger):
        calls.append(("configure_jul_to_python_logging", python_logger))

    monkeypatch.setattr(bridge.jpype, "isJVMStarted", fake_is_jvm_started)
    monkeypatch.setattr(bridge.jpype, "startJVM", fake_start_jvm)
    monkeypatch.setattr(bridge.jpype, "shutdownJVM", fake_shutdown_jvm)
    monkeypatch.setattr(bridge, "configure_jul_to_python_logging", fake_configure_jul)
    monkeypatch.setattr(bridge, "_prepend_java_home_to_path", lambda: None)

    with bridge.regi_session():
        # Inside the context: JVM must be up and logging must already be wired.
        assert jvm_state["started"] is True
        assert calls[0][0] == "startJVM"
        assert calls[1] == ("configure_jul_to_python_logging", bridge.logger)

    # On exit: JVM must have been shut down, and only after start+logging.
    assert [c[0] for c in calls] == [
        "startJVM",
        "configure_jul_to_python_logging",
        "shutdownJVM",
    ]
    assert jvm_state["started"] is False


def test_regi_session_propagates_body_exception_but_still_shuts_down_jvm(monkeypatch):
    """If the code inside the `with regi_session()` block raises, the JVM must still be shut down."""
    import regi_python.regi_python as bridge

    jvm_state = {"started": False}
    calls = []

    monkeypatch.setattr(bridge.jpype, "isJVMStarted", lambda: jvm_state["started"])

    def fake_start_jvm(*args, **kwargs):
        jvm_state["started"] = True
        calls.append("startJVM")

    def fake_shutdown_jvm():
        jvm_state["started"] = False
        calls.append("shutdownJVM")

    monkeypatch.setattr(bridge.jpype, "startJVM", fake_start_jvm)
    monkeypatch.setattr(bridge.jpype, "shutdownJVM", fake_shutdown_jvm)
    monkeypatch.setattr(bridge, "configure_jul_to_python_logging", lambda logger: None)
    monkeypatch.setattr(bridge, "_prepend_java_home_to_path", lambda: None)

    boom = RuntimeError("body exploded")
    with pytest.raises(RuntimeError) as excinfo:
        with bridge.regi_session():
            raise boom

    assert excinfo.value is boom
    assert calls == ["startJVM", "shutdownJVM"]
    assert jvm_state["started"] is False


def test_regi_session_reports_restart_failure_with_context(monkeypatch):
    """If startJVM fails after a prior shutdown, regi_session raises a clear, chained RuntimeError."""
    import regi_python.regi_python as bridge

    monkeypatch.setattr(bridge.jpype, "isJVMStarted", lambda: False)
    monkeypatch.setattr(
        bridge.jpype,
        "startJVM",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("JVM cannot be restarted")),
    )
    monkeypatch.setattr(bridge, "_prepend_java_home_to_path", lambda: None)

    with pytest.raises(RuntimeError) as excinfo:
        with bridge.regi_session():
            pass

    message = str(excinfo.value)
    assert "Failed to start the JVM for regi_session()." in message
    assert isinstance(excinfo.value.__cause__, OSError)
    assert str(excinfo.value.__cause__) == "JVM cannot be restarted"


def test_prepend_java_home_to_path_is_a_noop_without_java_home(monkeypatch):
    """With JAVA_HOME unset, PATH is left untouched."""
    import regi_python.regi_python as bridge

    monkeypatch.delenv("JAVA_HOME", raising=False)
    monkeypatch.setenv("PATH", "/usr/bin:/bin")

    bridge._prepend_java_home_to_path()

    assert os.environ["PATH"] == "/usr/bin:/bin"


def test_prepend_java_home_to_path_prepends_java_bin(monkeypatch):
    """With JAVA_HOME set and its bin/ not already on PATH, bin/ is prepended."""
    import regi_python.regi_python as bridge

    monkeypatch.setenv("JAVA_HOME", "/opt/java")
    monkeypatch.setenv("PATH", "/usr/bin:/bin")

    bridge._prepend_java_home_to_path()

    java_bin = os.path.join("/opt/java", "bin")
    assert os.environ["PATH"] == java_bin + os.pathsep + "/usr/bin:/bin"


def test_prepend_java_home_to_path_does_not_duplicate_existing_entry(monkeypatch):
    """If JAVA_HOME's bin/ is already on PATH, it is not added again."""
    import regi_python.regi_python as bridge

    java_bin = os.path.join("/opt/java", "bin")
    existing_path = java_bin + os.pathsep + "/usr/bin"

    monkeypatch.setenv("JAVA_HOME", "/opt/java")
    monkeypatch.setenv("PATH", existing_path)

    bridge._prepend_java_home_to_path()

    assert os.environ["PATH"] == existing_path