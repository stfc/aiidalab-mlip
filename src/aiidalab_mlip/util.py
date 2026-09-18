"""Contains utility functions used throughout the python package."""

from typing import TypeVar

import ipywidgets as ipw
from IPython.display import Javascript, display

AT = TypeVar("AT", ipw.Accordion, ipw.Tab)


def open_link_in_new_tab(path: str, _=None) -> None:
    """
    Open a given link in a new browser tab.

    Parameters
    ----------
    path :  str
        The link to be opened.
    """
    js_code = f"window.open('{path}', '_blank');"
    display(Javascript(js_code))


def tab_from_dict(typ: type[AT], tabs: dict[str, ipw.Widget]) -> AT:
    """Create a tab or accordion from a dict.

    Dict maps titles to widgets.

    Parameters
    ----------
    typ : type[ipw.Accordion | ipw.Tab]
        Accordion or Tab to create.
    tabs : dict[str, ipw.Widget]
        Dict of tabs to widgets.

    Returns
    -------
    Accordion or Tab
        Constructed Accordion or Tab.
    """
    blk = typ(list(tabs.values()))
    for ind, name in enumerate(tabs):
        blk.set_title(ind, name)

    return blk
