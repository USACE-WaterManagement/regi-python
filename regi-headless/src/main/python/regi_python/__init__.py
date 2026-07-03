from .regi_python import regi_session, run_headless
from importlib.metadata import version, PackageNotFoundError

__all__ = ["regi_session", "run_headless"]

try:
    __version__ = version("regi_python") # Use the 'name' from pyproject.toml
except PackageNotFoundError:
    # package is not installed
    __version__ = "unknown"