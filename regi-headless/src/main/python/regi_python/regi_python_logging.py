import os
import logging
from jpype import JImplements, JOverride

_java_log_sink = None


def _get_log_level():
    log_level_name = os.environ.get("REGI_LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, None)
    invalid_log_level = not isinstance(log_level, int)
    if invalid_log_level:
        log_level = logging.INFO
    return log_level, invalid_log_level, log_level_name


def configure_logging():
    log_level, invalid_log_level, log_level_name = _get_log_level()

    log_format = os.environ.get(
        "REGI_LOG_FORMAT",
        "%(asctime)s %(levelname)s %(name)s "
        "[job=%(aws_batch_job_id)s attempt=%(aws_batch_job_attempt)s] - %(message)s",
    )

    class AwsBatchFilter(logging.Filter):
        def filter(self, record):
            record.aws_batch_job_id = os.environ.get("AWS_BATCH_JOB_ID", "-")
            record.aws_batch_job_attempt = os.environ.get("AWS_BATCH_JOB_ATTEMPT", "-")
            return True

    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter(log_format))
    handler.addFilter(AwsBatchFilter())

    logger = logging.getLogger("regi-launcher")
    logger.setLevel(log_level)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False

    if invalid_log_level:
        logger.warning("Invalid REGI_LOG_LEVEL '%s'; using INFO.", log_level_name)

    return logger


def configure_jul_to_python_logging(python_logger):
    global _java_log_sink

    from java.util.logging import Logger
    from usace.rowcps.headless import PythonJulHandler

    java_level = _python_level_to_jul_level(python_logger.getEffectiveLevel())

    root_logger = Logger.getLogger("")
    root_logger.setLevel(java_level)

    for handler in root_logger.getHandlers():
        root_logger.removeHandler(handler)

    PythonLogSink = _create_python_log_sink_class()
    _java_log_sink = PythonLogSink(python_logger)

    handler = PythonJulHandler(_java_log_sink)
    handler.setLevel(java_level)

    root_logger.addHandler(handler)


def _python_level_to_jul_level(python_level):
    from java.util.logging import Level

    if python_level <= logging.NOTSET:
        return Level.ALL
    if python_level <= logging.DEBUG:
        return Level.FINE
    if python_level <= logging.INFO:
        return Level.INFO
    if python_level <= logging.WARNING:
        return Level.WARNING
    if python_level <= logging.CRITICAL:
        return Level.SEVERE
    return Level.OFF


def _jul_level_to_python_level(jul_level_name):
    mapping = {
        "SEVERE": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "CONFIG": logging.INFO,
        "FINE": logging.DEBUG,
        "FINER": logging.DEBUG,
        "FINEST": logging.DEBUG,
        "ALL": logging.NOTSET,
        "OFF": logging.CRITICAL + 10,
    }
    return mapping.get(str(jul_level_name), logging.INFO)


def _create_python_log_sink_class():
    # JPype resolves @JImplements interfaces immediately, so define this class only
    # after the JVM has started; otherwise importing this module would fail.
    from jpype import JImplements, JOverride

    @JImplements("usace.rowcps.headless.PythonLogSink")
    class PythonLogSink:
        def __init__(self, python_logger):
            self._logger = python_logger

        @JOverride
        def log(self, record, message):
            level = _jul_level_to_python_level(record.getLevel().getName())
            name = str(record.getLoggerName() or "java")
            message = str(message)

            thrown = record.getThrown()
            if thrown is not None:
                message = f"{message}\n{thrown}"

            self._logger.log(level, "[%s] %s", name, message)

    return PythonLogSink