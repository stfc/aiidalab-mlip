"""Test package import and versioning."""

import aiidalab_mlip


def test_package_version():
    """Test that package defines a valid __version__ string."""
    assert hasattr(aiidalab_mlip, "__version__")
    assert isinstance(aiidalab_mlip.__version__, str)
    assert len(aiidalab_mlip.__version__) > 0
