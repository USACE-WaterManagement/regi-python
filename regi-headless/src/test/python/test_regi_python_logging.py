"""
JUL-to-Python log sink behavior for regi_python.regi_python_logging.

Covers:
  * the generated PythonLogSink forwards Java log records into the Python
    logger at the right level, tagged with the originating Java logger name,
    and with any stack trace appended to the message.
"""

import logging


def test_python_log_sink_appends_java_stack_trace(monkeypatch):
    """A SEVERE Java log record with a stack trace is forwarded as an ERROR with the trace appended."""
    import regi_python.regi_python_logging as logging_bridge

    monkeypatch.setattr(
        logging_bridge.jpype,
        "JImplements",
        lambda *args, **kwargs: (lambda cls: cls),
    )
    monkeypatch.setattr(logging_bridge.jpype, "JOverride", lambda func: func)

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
