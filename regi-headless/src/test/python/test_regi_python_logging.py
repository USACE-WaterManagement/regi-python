"""
JUL-to-Python log sink behavior for regi_python.regi_python_logging.

Covers:
  * the generated PythonLogSink forwards Java log records into the Python
    logger at the right level, tagged with the originating Java logger name,
    with any stack trace appended to the message (and omitted when there
    isn't one).
  * configure_logging() falls back to INFO and warns on an invalid
    REGI_LOG_LEVEL, and its AwsBatchFilter stamps AWS Batch env vars (or
    "-" defaults) onto every log record.
  * _python_level_to_jul_level() maps every Python logging threshold to the
    expected java.util.logging.Level constant.
  * configure_jul_to_python_logging() clears existing JUL handlers on the
    Java root logger and installs a Python-backed sink handler at the
    correct level.
"""

import logging
import sys
import types

import pytest


def _patch_jimplements(monkeypatch, logging_bridge):
    """@JImplements/@JOverride are no-ops here; we only need the plain class."""
    monkeypatch.setattr(logging_bridge.jpype, "JImplements", lambda *a, **k: (lambda cls: cls))
    monkeypatch.setattr(logging_bridge.jpype, "JOverride", lambda func: func)


def test_python_log_sink_appends_java_stack_trace(monkeypatch):
    """A SEVERE Java log record with a stack trace is forwarded as an ERROR with the trace appended."""
    import regi_python.regi_python_logging as logging_bridge

    _patch_jimplements(monkeypatch, logging_bridge)

    class FakeLevel:
        def getName(self):
            return "SEVERE"

    class FakeRecord:
        def getLevel(self):
            return FakeLevel()

        def getLoggerName(self):
            return "usace.rowcps.headless.tests"

    class FakeLogger:
        def __init__(self):
            self.calls = []

        def log(self, level, fmt, *args):
            self.calls.append((level, fmt, args))

    fake_logger = FakeLogger()
    sink_class = logging_bridge._create_python_log_sink_class()
    sink = sink_class(fake_logger)

    sink.log(FakeRecord(), "Execution failed.", "java.lang.RuntimeException: boom")

    assert fake_logger.calls == [
        (
            logging.ERROR,
            "[%s] %s",
            (
                "usace.rowcps.headless.tests",
                "Execution failed.\njava.lang.RuntimeException: boom",
            ),
        )
    ]


def test_python_log_sink_without_stack_trace_omits_appended_trace(monkeypatch):
    """A Java log record with no stack trace is forwarded without an appended trace line."""
    import regi_python.regi_python_logging as logging_bridge

    _patch_jimplements(monkeypatch, logging_bridge)

    class FakeLevel:
        def getName(self):
            return "INFO"

    class FakeRecord:
        def getLevel(self):
            return FakeLevel()

        def getLoggerName(self):
            return "usace.rowcps.headless.tests"

    class FakeLogger:
        def __init__(self):
            self.calls = []

        def log(self, level, fmt, *args):
            self.calls.append((level, fmt, args))

    fake_logger = FakeLogger()
    sink_class = logging_bridge._create_python_log_sink_class()
    sink = sink_class(fake_logger)

    sink.log(FakeRecord(), "Started normally.", None)

    assert fake_logger.calls == [
        (logging.INFO, "[%s] %s", ("usace.rowcps.headless.tests", "Started normally."))
    ]


def test_configure_logging_falls_back_to_info_on_invalid_level(monkeypatch):
    """An invalid REGI_LOG_LEVEL falls back to INFO and logs a warning about the fallback."""
    import regi_python.regi_python_logging as logging_bridge

    monkeypatch.setenv("REGI_LOG_LEVEL", "NOT_A_LEVEL")

    warnings = []
    monkeypatch.setattr(
        logging.Logger,
        "warning",
        lambda self, msg, *args, **kwargs: warnings.append((msg, args)),
    )

    logger = logging_bridge.configure_logging()

    assert logger.level == logging.INFO
    assert logger.handlers[0].level == logging.INFO
    assert warnings == [("Invalid REGI_LOG_LEVEL '%s'; using INFO.", ("NOT_A_LEVEL",))]


def test_configure_logging_accepts_a_valid_level_without_warning(monkeypatch):
    """A valid REGI_LOG_LEVEL is honored and no fallback warning is logged."""
    import regi_python.regi_python_logging as logging_bridge

    monkeypatch.setenv("REGI_LOG_LEVEL", "debug")

    warnings = []
    monkeypatch.setattr(
        logging.Logger,
        "warning",
        lambda self, msg, *args, **kwargs: warnings.append((msg, args)),
    )

    logger = logging_bridge.configure_logging()

    assert logger.level == logging.DEBUG
    assert warnings == []


def test_configure_logging_aws_batch_filter_defaults_and_reflects_env(monkeypatch):
    """AwsBatchFilter stamps AWS Batch env vars onto records, defaulting to '-' when unset."""
    import regi_python.regi_python_logging as logging_bridge

    monkeypatch.delenv("AWS_BATCH_JOB_ID", raising=False)
    monkeypatch.delenv("AWS_BATCH_JOB_ATTEMPT", raising=False)

    logger = logging_bridge.configure_logging()
    handler = logger.handlers[0]
    batch_filter = handler.filters[0]

    record = logging.LogRecord("regi-launcher", logging.INFO, __file__, 1, "hello", None, None)

    assert batch_filter.filter(record) is True
    assert record.aws_batch_job_id == "-"
    assert record.aws_batch_job_attempt == "-"

    monkeypatch.setenv("AWS_BATCH_JOB_ID", "job-123")
    monkeypatch.setenv("AWS_BATCH_JOB_ATTEMPT", "2")

    assert batch_filter.filter(record) is True
    assert record.aws_batch_job_id == "job-123"
    assert record.aws_batch_job_attempt == "2"


def _install_fake_java_util_logging(monkeypatch):
    """Patch sys.modules so `from java.util.logging import ...` resolves to fakes."""
    level_ns = types.SimpleNamespace(
        ALL="ALL", FINE="FINE", INFO="INFO", WARNING="WARNING", SEVERE="SEVERE", OFF="OFF"
    )

    class FakeRootLogger:
        def __init__(self):
            self.level = None
            self.handlers = ["existing-handler-1", "existing-handler-2"]
            self.removed = []
            self.added = []

        def setLevel(self, level):
            self.level = level

        def getHandlers(self):
            return list(self.handlers)

        def removeHandler(self, handler):
            self.removed.append(handler)
            if handler in self.handlers:
                self.handlers.remove(handler)

        def addHandler(self, handler):
            self.added.append(handler)
            self.handlers.append(handler)

    fake_root_logger = FakeRootLogger()

    class FakeLogger:
        @staticmethod
        def getLogger(name):
            assert name == ""
            return fake_root_logger

    jul_module = types.ModuleType("java.util.logging")
    jul_module.Logger = FakeLogger
    jul_module.Level = level_ns
    monkeypatch.setitem(sys.modules, "java.util.logging", jul_module)

    return fake_root_logger, level_ns


def _install_fake_python_jul_handler(monkeypatch):
    created_handlers = []

    class FakePythonJulHandler:
        def __init__(self, sink):
            self.sink = sink
            self.level = None
            created_handlers.append(self)

        def setLevel(self, level):
            self.level = level

    headless_module = types.ModuleType("usace.rowcps.headless")
    headless_module.PythonJulHandler = FakePythonJulHandler
    monkeypatch.setitem(sys.modules, "usace.rowcps.headless", headless_module)

    return created_handlers


@pytest.mark.parametrize(
    "python_level, expected_attr",
    [
        (logging.NOTSET, "ALL"),
        (logging.DEBUG, "FINE"),
        (logging.INFO, "INFO"),
        (logging.WARNING, "WARNING"),
        (logging.ERROR, "SEVERE"),
        (logging.CRITICAL, "SEVERE"),
        (logging.CRITICAL + 10, "OFF"),
    ],
)
def test_python_level_to_jul_level_maps_each_threshold(monkeypatch, python_level, expected_attr):
    """Every Python logging threshold maps to the expected java.util.logging.Level constant."""
    import regi_python.regi_python_logging as logging_bridge

    _, level_ns = _install_fake_java_util_logging(monkeypatch)

    result = logging_bridge._python_level_to_jul_level(python_level)

    assert result == getattr(level_ns, expected_attr)


def test_configure_jul_to_python_logging_wires_root_logger_and_sink(monkeypatch):
    """configure_jul_to_python_logging clears existing JUL handlers and installs a Python-backed sink."""
    import regi_python.regi_python_logging as logging_bridge

    _patch_jimplements(monkeypatch, logging_bridge)
    monkeypatch.setattr(logging_bridge, "_java_log_sink", None)

    fake_root_logger, level_ns = _install_fake_java_util_logging(monkeypatch)
    created_handlers = _install_fake_python_jul_handler(monkeypatch)

    python_logger = logging.getLogger("test-regi-launcher")
    python_logger.setLevel(logging.DEBUG)

    logging_bridge.configure_jul_to_python_logging(python_logger)

    # Existing JUL handlers on the Java root logger are cleared out.
    assert fake_root_logger.removed == ["existing-handler-1", "existing-handler-2"]

    # The root logger and the new handler are both set to the mapped level (DEBUG -> FINE).
    assert fake_root_logger.level == level_ns.FINE
    assert len(created_handlers) == 1
    new_handler = created_handlers[0]
    assert new_handler.level == level_ns.FINE

    # The new handler is the one actually added to the root logger.
    assert fake_root_logger.added == [new_handler]

    # The handler wraps a PythonLogSink backed by the Python logger we passed in.
    assert new_handler.sink._logger is python_logger
    assert logging_bridge._java_log_sink is new_handler.sink
