"""Runtime bridge for executing REGI calculations from Python."""

import os
import jpype
import jpype.imports
from contextlib import contextmanager
from .regi_python_logging import configure_logging, configure_jul_to_python_logging

logger = configure_logging()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_PATH = os.path.join(BASE_DIR, "lib", "*")

@contextmanager
def regi_session():
    """
    Start the JVM on entry and shut it down when the context exits.
    """
    started_jvm = False
    if not jpype.isJVMStarted():
        _prepend_java_home_to_path()
        logger.info("Starting JVM...")
        jpype.startJVM(
            jpype.getDefaultJVMPath(),
            convertStrings=True,
            classpath=[LIB_PATH]
        )
        configure_jul_to_python_logging(logger)
        started_jvm = True

    try:
        yield
    finally:
        if started_jvm and jpype.isJVMStarted():
            logger.info("Shutting down JVM...")
            jpype.shutdownJVM()

def run_headless(calculation_callback):
    """Run a callback against a headless REGI domain."""
    _require_environment_variables("CDA_URL", "CDA_API_KEY", "OFFICE_ID")

    # Import these only after the JVM has started.
    from usace.rowcps.headless import HeadlessRegiDomainFactory, RegiCalcRegistry
    from usace.rowcps.regi.factories import RowcpsExecutorService
    from java.util.concurrent import TimeUnit
    factory = HeadlessRegiDomainFactory()
    logger.info("Attempting to create RegiDomain...")
    regi_domain = factory.createDomain()
    manager_id = factory.getManagerId()
    registry = RegiCalcRegistry(regi_domain, manager_id)

    try:
        logger.info("Executing callback...")
        calculation_callback(registry)
        regi_domain.commitData(manager_id)
    except Exception as e:
        logger.error("Execution failed.", exc_info=True)
        raise
    finally:
        _shutdown_executor(manager_id)
        regi_domain.closing()


def _require_environment_variables(*variable_names):
    missing = [name for name in variable_names if not os.environ.get(name)]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )


def _prepend_java_home_to_path():
    java_home = os.environ.get("JAVA_HOME")
    if not java_home:
        return

    java_bin = os.path.join(java_home, "bin")
    path = os.environ.get("PATH", "")
    if java_bin not in path:
        os.environ["PATH"] = java_bin + os.pathsep + path


def _shutdown_executor(manager_id):
    from usace.rowcps.regi.factories import RowcpsExecutorService
    from java.util.concurrent import TimeUnit
    res = RowcpsExecutorService.getInstance(manager_id)
    res.shutdown()
    if not res.awaitTermination(3000, TimeUnit.MILLISECONDS):
        res.shutdownNow()
