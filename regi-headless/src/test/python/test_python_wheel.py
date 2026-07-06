#  Copyright (c) 2026
#  United States Army Corps of Engineers - Hydrologic Engineering Center (USACE/HEC)
#  All Rights Reserved.  USACE PROPRIETARY/CONFIDENTIAL.
#  Source may not be released without written approval from HEC

import importlib.metadata
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


def test_bundled_java_libraries_are_present():
    import regi_python
    package_dir = Path(regi_python.__file__).parent
    lib_dir = package_dir / "lib"

    assert lib_dir.is_dir()
    assert any(lib_dir.glob("*.jar"))
