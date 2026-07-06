#  Copyright (c) 2026
#  United States Army Corps of Engineers - Hydrologic Engineering Center (USACE/HEC)
#  All Rights Reserved.  USACE PROPRIETARY/CONFIDENTIAL.
#  Source may not be released without written approval from HEC

import os
import logging
import jpype
import jpype.imports
from contextlib import contextmanager
from pathlib import Path
from .regi_python_logging import configure_logging

logger = configure_logging()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_PATH = os.path.join(BASE_DIR, "lib", "*")
java_home = os.environ.get('JAVA_HOME')
java_bin = os.path.join(java_home, 'bin')
if java_bin not in os.environ['PATH']:
    os.environ['PATH'] = java_bin + os.pathsep + os.environ['PATH']

@contextmanager
def regi_session():
    """
    Context manager to handle JVM lifecycle. 
    Usage:
        with regi_session():
            run_headless(my_func)
    """
    if not jpype.isJVMStarted():
        logger.info("Starting JVM...")
        jpype.startJVM(
            jpype.getDefaultJVMPath(),
            convertStrings=True,
            classpath=[LIB_PATH]
        )

    try:
        yield
    finally:
        if jpype.isJVMStarted():
            logger.info("Shutting down JVM...")
            jpype.shutdownJVM()

def run_headless(calculation_callback):
    # We must import these inside the function or after JVM starts
    from usace.rowcps.headless import HeadlessRegiDomainFactory, RegiCalcRegistry
    from usace.rowcps.regi.factories import RowcpsExecutorService
    from java.util.concurrent import TimeUnit
    factory = HeadlessRegiDomainFactory()
    logger.info("Attempting to create RegiDomain...")
    regi_domain = factory.createDomain()

    if regi_domain is not None:
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

def _shutdown_executor(manager_id):
    from usace.rowcps.regi.factories import RowcpsExecutorService
    from java.util.concurrent import TimeUnit
    res = RowcpsExecutorService.getInstance(manager_id)
    res.shutdown()
    if not res.awaitTermination(3000, TimeUnit.MILLISECONDS):
        res.shutdownNow()