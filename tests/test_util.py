"""Test utility functions."""

from unittest.mock import patch

import ipywidgets as ipw
from aiidalab_mlip.util import open_link_in_new_tab, tab_from_dict


def test_open_link_in_new_tab():
    """Test open_link_in_new_tab calls display with Javascript code."""
    with patch("aiidalab_mlip.util.display") as mock_display:
        open_link_in_new_tab("https://example.com")
        mock_display.assert_called_once()
        arg = mock_display.call_args[0][0]
        assert "window.open('https://example.com', '_blank');" in arg.data


def test_tab_from_dict():
    """Test creating a Tab widget from dictionary."""
    tabs = {
        "First": ipw.HTML("<p>First</p>"),
        "Second": ipw.HTML("<p>Second</p>"),
    }
    tab_widget = tab_from_dict(ipw.Tab, tabs)
    assert isinstance(tab_widget, ipw.Tab)
    assert len(tab_widget.children) == 2
    assert tab_widget.get_title(0) == "First"
    assert tab_widget.get_title(1) == "Second"


def test_accordion_from_dict():
    """Test creating an Accordion widget from dictionary."""
    tabs = {
        "Section A": ipw.HTML("<p>A</p>"),
        "Section B": ipw.HTML("<p>B</p>"),
    }
    accordion = tab_from_dict(ipw.Accordion, tabs)
    assert isinstance(accordion, ipw.Accordion)
    assert len(accordion.children) == 2
    assert accordion.get_title(0) == "Section A"
    assert accordion.get_title(1) == "Section B"
