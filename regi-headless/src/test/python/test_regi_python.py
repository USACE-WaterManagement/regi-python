"""
Packaging and public-API smoke tests for regi_python.

Covers:
  * the built wheel installs with correct distribution metadata and bundles
    its Java libraries.
  * the top-level package imports cleanly and exposes regi_session and
    run_headless as its public API.
  * run_headless fails fast with a clear error when required CDA env vars
    are missing.
  * the bridge module can be imported/reloaded without JAVA_HOME set.

regi_session/run_headless runtime *state* behavior (JVM lifecycle, commit,
shutdown, closing, exception propagation) lives in test_regi_python_runtime.py.
"""

import importlib.metadata
import importlib
from pathlib import Path


def test_wheel_distribution_metadata_is_installed():
    """The installed wheel reports the expected distribution name and a version."""
    dist = importlib.metadata.distribution("regi-python")

    assert dist.metadata["Name"] == "regi-python"
    assert dist.version


def test_wheel_can_import_top_level_package():
    """The top-level regi_python package imports successfully."""
    import regi_python

    assert regi_python is not None


def test_public_api_is_exposed():
    """regi_session and run_headless are exposed as the package's public API."""
    import regi_python

    assert callable(regi_python.regi_session)
    assert callable(regi_python.run_headless)


def test_run_headless_requires_cda_environment(monkeypatch):
    """run_headless fails fast with a clear message when CDA env vars are missing."""
    import regi_python

    monkeypatch.delenv("CDA_URL", raising=False)
    monkeypatch.delenv("CDA_API_KEY", raising=False)
    monkeypatch.delenv("OFFICE_ID", raising=False)

    try:
        regi_python.run_headless(lambda registry: None)
    except RuntimeError as exc:
        assert str(exc) == (
            "Missing required environment variables: CDA_URL, CDA_API_KEY, OFFICE_ID"
        )
    else:
        raise AssertionError("run_headless should fail when CDA env vars are missing")


def test_bundled_java_libraries_are_present():
    """The package ships a lib/ directory containing at least one bundled jar."""
    import regi_python
    package_dir = Path(regi_python.__file__).parent
    lib_dir = package_dir / "lib"

    assert lib_dir.is_dir()
    assert any(lib_dir.glob("*.jar"))


def test_bridge_import_does_not_require_java_home(monkeypatch):
    """The bridge module imports/reloads cleanly even without JAVA_HOME set."""
    import regi_python.regi_python as bridge

    monkeypatch.delenv("JAVA_HOME", raising=False)

    reloaded = importlib.reload(bridge)

    assert reloaded is bridge
