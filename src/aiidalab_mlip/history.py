"""Defines the process history applicaion page."""

from datetime import datetime

from aiidalab_widgets_base import ProcessNodesTreeWidget
import ipywidgets as ipw
from aiida_mlip.calculations.geomopt import GeomOpt
from aiida_mlip.calculations.md import MD
from aiida_mlip.calculations.singlepoint import Singlepoint
from alc_aiidalab_widgets.widgets import AiiDADatabaseQueryWidget
from IPython.display import display
from traitlets import HasTraits, Unicode

from aiidalab_mlip.common.navigation import QuickAccessButtons
from aiidalab_mlip.common.node_viewers import CustomAiidaNodeViewWidget


class HistoryApp:
    """The process history page's main app."""

    def __init__(self):
        """HistoryApp constructor."""
        self.view = HistoryAppView()
        display(self.view)


class HistoryAppView(ipw.VBox):
    """Main view for the process history page."""

    def __init__(self, **kwargs) -> None:
        """
        HistoryAppView Constructor.

        Parameters
        ----------
        model : HistoryModel
            The MVC model component to associate with this view app.
        """

        logo = ipw.HTML(
            """
            <div class="app-container logo" style="text-align: center;">
                <h1> Machine Learning Interatomic Potentials</h1>
            </div>
            """,
            layout={"margin": "auto"},
        )

        subtitle = ipw.HTML(
            """
            <h2 style="text-align: center;">
            Access historical data from nodes.
            </h2>
            """
        )

        nav_btns = QuickAccessButtons()

        header = ipw.VBox(
            children=[
                logo,
                subtitle,
            ],
            layout={"margin": "auto"},
        )

        footer = ipw.HTML(
            f"""
            <footer>
                Copyright (c) {datetime.now().year} MLIP Development Team
            </footer>
            """,
            layout={"align-content": "right"},
        )

        self.guide = ipw.HTML(
            """
            <h3>ChemShell Process History</h3>
            <p>
            Search through past processes and visualise inputs, outputs and
            provenance relationships.
            </p>
            """
        )
        self.lookup_widget = AiiDADatabaseQueryWidget(
            "Process Lookup",
            [
                GeomOpt,
                Singlepoint,
                MD,
            ],
        )
        self.lookup_widget.observe(self._update_node_view, "data_object")

        self.node_tree = ProcessNodesTreeWidget()
        self.node_view = CustomAiidaNodeViewWidget()
        ipw.dlink(
            (self.node_tree, "selected_nodes"),
            (self.node_view, "node"),
            transform=lambda nodes: nodes[0] if nodes else None,
        )

        super().__init__(
            layout={},
            children=[
                header,
                nav_btns,
                self.guide,
                self.lookup_widget,
                self.node_tree,
                self.node_view,
                footer,
            ],
            **kwargs,
        )

    def _update_node_view(self, _) -> None:
        """Update the node view to the currently selected process node."""
        if self.lookup_widget.data_object is not None:
            self.node_tree.value = self.lookup_widget.data_object.uuid
