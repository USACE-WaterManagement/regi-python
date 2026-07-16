#  Copyright (c) 2026
#  United States Army Corps of Engineers - Hydrologic Engineering Center (USACE/HEC)
#  All Rights Reserved.  USACE PROPRIETARY/CONFIDENTIAL.
#  Source may not be released without written approval from HEC

import importlib.metadata
import importlib
from pathlib import Path


def test_wheel_distribution_metadata_is_installed():
    dist = importlib.metadata.distribution("regi-python")

    assert dist.metadata["Name"] == "regi-python"
    assert dist.version


def test_wheel_can_import_top_level_package():
    import regi_python

    assert regi_python is not None


def test_public_api_is_exposed():
    import regi_python

    assert callable(regi_python.regi_session)
    assert callable(regi_python.run_headless)


def test_run_headless_requires_cda_environment(monkeypatch):
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
    import regi_python
    package_dir = Path(regi_python.__file__).parent
    lib_dir = package_dir / "lib"

    assert lib_dir.is_dir()
    assert any(lib_dir.glob("*.jar"))


def test_bridge_import_does_not_require_java_home(monkeypatch):
    import regi_python.regi_python as bridge

    monkeypatch.delenv("JAVA_HOME", raising=False)

    reloaded = importlib.reload(bridge)

    assert reloaded is bridge


def test_regi_session_only_shuts_down_jvm_it_started(monkeypatch):
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
