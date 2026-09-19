"""Test navigation controls."""

import ipywidgets as ipw
from aiidalab_mlip.common.navigation import QuickAccessButtons


def test_quick_access_buttons():
    """Test QuickAccessButtons initialization and children buttons."""
    buttons = QuickAccessButtons()
    assert isinstance(buttons, ipw.HBox)
    assert len(buttons.children) == 4

    btn_descriptions = [b.description for b in buttons.children]
    assert "New Calculation" in btn_descriptions
    assert "History" in btn_descriptions
    assert "Setup Resources" in btn_descriptions
    assert "Documentation" in btn_descriptions

    # Verify buttons have tooltips and icons
    assert buttons.new_calc_link.icon == "plus"
    assert buttons.history_link.icon == "history"
    assert buttons.resource_setup_link.icon == "cogs"
    assert buttons.docs_link.icon == "book"
