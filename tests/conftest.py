"""Pytest configuration and fixtures for aiidalab-mlip tests."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock
import pytest


# Mock external dependencies that might not be installed in lightweight test environments
class MockClass:
    """Generic class mock for traitlet klass targets."""

    def __init__(self, *args, **kwargs):
        pass


MOCK_MODULES = [
    "aiida",
    "aiida.orm",
    "aiida_mlip",
    "aiida_mlip.data",
    "aiida_mlip.data.model",
    "aiida_mlip.calculations",
    "aiida_mlip.calculations.singlepoint",
    "aiida_mlip.calculations.geomopt",
    "aiida_mlip.calculations.md",
    "alc_aiidalab_widgets",
    "alc_aiidalab_widgets.widgets",
    "alc_aiidalab_widgets.types",
    "aiidalab_widgets_base",
    "nglview",
]

for mod in MOCK_MODULES:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

# Traitlets Instance(klass=...) requires actual type objects
if not hasattr(sys.modules["aiida.orm"], "Code") or isinstance(
    sys.modules["aiida.orm"].Code, MagicMock
):
    sys.modules["aiida.orm"].Code = MockClass

if not hasattr(sys.modules["aiida.orm"], "StructureData") or isinstance(
    sys.modules["aiida.orm"].StructureData, MagicMock
):
    sys.modules["aiida.orm"].StructureData = MockClass

if not hasattr(sys.modules["aiida_mlip.data.model"], "ModelData") or isinstance(
    sys.modules["aiida_mlip.data.model"].ModelData, MagicMock
):
    sys.modules["aiida_mlip.data.model"].ModelData = MockClass

if not hasattr(sys.modules["alc_aiidalab_widgets.types"], "HasStatus") or isinstance(
    sys.modules["alc_aiidalab_widgets.types"].HasStatus, MagicMock
):
    sys.modules["alc_aiidalab_widgets.types"].HasStatus = MockClass


@pytest.fixture
def dummy_app_paths():
    """Return standard test app paths."""
    return {
        "appbase": "/apps/apps/aiidalab-mlip",
        "jupbase": "/jupyter",
        "notebase": "main.ipynb",
    }
