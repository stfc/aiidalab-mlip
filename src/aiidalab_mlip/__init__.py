"""AiiDAlab MLIP application package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("aiidalab-mlip")
except PackageNotFoundError:
    __version__ = "unknown"
