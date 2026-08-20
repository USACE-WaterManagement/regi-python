"""
Starts the one JVM this pytest session gets, before any individual test
module's own JVM-start logic runs.

JPype allows only a single JVM per process, and its classpath is fixed at
startup. Two test modules under this directory start a real JVM:

  * test_datetime_instant_conversion.py needs no project jars -- it only
    touches java.time, which ships in every JDK.
  * test_district_scripts.py reflects over the compiled REGI Headless
    classes (ScriptableInflowImpl, etc.), so it needs those jars on the
    classpath.
"""

import os
from pathlib import Path

import jpype
import pytest

# .../regi-headless/regi-headless (the Gradle module root, three levels up
# from this file's directory: src/test/python -> src/test -> src -> module root)
MODULE_ROOT = Path(__file__).resolve().parents[3]


def _discover_classpath():
    """
    Locates the REGI Headless jars for the classpath.

    Gradle knows this path authoritatively (see `smokeTestDistrictScripts`
    in build.gradle, which sets REGI_HEADLESS_JAVA_LIB_DIR) and passes it in
    as an environment variable. The fallbacks below
    -- an installed `regi_python` wheel, then the raw `bundlePython` build
    output -- only exist so the JVM still gets a useful classpath when this
    test is run outside Gradle (e.g. directly from an IDE).
    """
    env_lib_dir = os.environ.get("REGI_HEADLESS_JAVA_LIB_DIR")
    if env_lib_dir:
        lib_dir = Path(env_lib_dir)
        if lib_dir.is_dir() and any(lib_dir.glob("*.jar")):
            return str(lib_dir / "*")
        return None

    candidate_lib_dirs = []

    try:
        import regi_python
    except ImportError:
        pass
    else:
        candidate_lib_dirs.append(Path(regi_python.__file__).resolve().parent / "lib")

    candidate_lib_dirs.append(
        MODULE_ROOT / "build" / "install" / "regi_python" / "regi_python" / "lib"
    )

    for lib_dir in candidate_lib_dirs:
        if lib_dir.is_dir() and any(lib_dir.glob("*.jar")):
            return str(lib_dir / "*")
    return None


@pytest.fixture(scope="session", autouse=True)
def _session_jvm():
    if jpype.isJVMStarted():
        yield
        return

    classpath = _discover_classpath()
    try:
        if classpath:
            jpype.startJVM(jpype.getDefaultJVMPath(), classpath=[classpath])
        else:
            jpype.startJVM(jpype.getDefaultJVMPath())
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"No usable JVM available for jpype: {exc}")
    yield
    # Deliberately not shut down: a JVM cannot be restarted once stopped in
    # the same process, and other test modules in this session may still
    # need it.
