"""Test start widget for AiiDAlab home page."""

import ipywidgets as ipw
from start import get_start_widget


def test_get_start_widget(dummy_app_paths):
    """Test that get_start_widget produces valid HTML with app link."""
    widget = get_start_widget(
        dummy_app_paths["appbase"],
        dummy_app_paths["jupbase"],
        dummy_app_paths["notebase"],
    )
    assert isinstance(widget, ipw.HTML)
    assert "Machine Learning Interatomic Potentials (MLIP)" in widget.value
    assert f'{dummy_app_paths["appbase"]}/main.ipynb' in widget.value
    assert "Launch MLIP App" in widget.value
