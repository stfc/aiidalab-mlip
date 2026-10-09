"""Results viewing wizard step."""
import traceback

import ipywidgets as ipw
from aiida import orm
from aiida.orm import (
    ProcessNode,
    QueryBuilder,
)
from aiidalab_widgets_base import ProcessNodesTreeWidget, WizardAppWidgetStep
from alc_aiidalab_widgets.layouts import Step
from alc_aiidalab_widgets.types import CallbackDict

from aiidalab_mlip.common.node_viewers import CustomAiidaNodeViewWidget


class ResultsWizardStep(Step, WizardAppWidgetStep):
    """Wizard step for viewing results."""

    DEBUG_TABLE_FMT = "{pk:<6} {type:<15} {state:<12} {exit:<6} {created}"

    def __init__(self, **kwargs):
        """
        Initialize results wizard step.

        Parameters
        ----------
        model : ResultsModel
            The results data model
        """
        # Process list refresh button
        self.refresh_button = ipw.Button(
            description="Refresh Process List",
            button_style="primary",
            icon="refresh",
            layout={"margin": "auto", "width": "60%"},
        )
        self.refresh_button.on_click(self._on_refresh_click)

        # Process selector dropdown
        self.process_selector = ipw.Select(
            options=[],
            description="Node:",
            disabled=False,
            layout={"margin": "auto", "width": "60%"},
        )
        self.process_selector.observe(self._on_process_select, names="value")

        # Manual PK input (alternative to dropdown)
        self.pk_input = ipw.IntText(
            value=0,
            description="Or enter PK:",
            disabled=False,
            layout={"margin": "auto", "width": "60%"},
        )

        self.load_button = ipw.Button(
            description="Load Results",
            button_style="info",
            layout={"margin": "auto", "width": "20%"},
        )
        self.load_button.on_click(self._on_load_click)

        self.node_tree = ProcessNodesTreeWidget()
        self.node_view = CustomAiidaNodeViewWidget()
        ipw.dlink(
            (self.node_tree, "selected_nodes"),
            (self.node_view, "node"),
            transform=lambda nodes: nodes[0] if nodes else None,
        )

        self.update_btn = ipw.Button(
            description="Refresh",
            icon="arrows-rotate",
            disabled=False,
            button_style="info",
            tooltip="Refresh process information.",
            layout={"margin": "auto", "width": "70%"},
        )
        self.update_btn.on_click(self._update_node)

        super().__init__(
            title="View Results",
            info="View the progress and results of the generated MLIP workflow.",
            widgets=[
                self.refresh_button,
                self.process_selector,
                self.pk_input,
                self.load_button,
                self.node_tree,
                self.node_view,
                self.update_btn,
            ],
            submittable=False,
            **kwargs,
        )

    def _handle_displayed(self, **kwargs):
        self._refresh_process_list()
        super()._handle_displayed(**kwargs)

    def _update_node(self, _) -> None:
        """Refresh the process information."""
        self.node_tree.update()

    def _on_refresh_click(self, _) -> None:
        """Refresh the process list."""
        self._refresh_process_list()

    def _refresh_process_list(self) -> None:
        """Load and display recent processes."""
        with self.logspace:
            self.logspace.clear_output()

            # Query recent calculations
            qb = QueryBuilder()
            qb.append(
                ProcessNode,
                filters={"attributes.process_label": {"in": ["Singlepoint", "GeomOpt", "MD"]}},
                project=[
                    "id",
                    "ctime",
                    "attributes.process_label",
                    "attributes.process_state",
                    "attributes.exit_status",
                ],
            )
            qb.order_by({ProcessNode: {"ctime": "desc"}})

            try:
                results = qb.all()
            except Exception as e:
                print(f"Error loading processes: {e}")

                traceback.print_exc()

            if not results:
                self.status.failure("No MLIP calculations found. Submit one in Step 4!")
                self.process_selector.options = []
                return

            options = []

            for pk, ctime, label, _state, exit_status in results:
                status_icon = "OK" if exit_status == 0 else "ERR" if exit_status else "RUN"
                time_str = ctime.strftime("%Y-%m-%d %H:%M")

                # Add to select options
                display = f"PK {pk} - {label} ({status_icon}) - {time_str}"
                options.append((display, pk))

            self.process_selector.options = options
            if options:
                self.process_selector.value = options[0][1]  # Select most recent

    def _on_process_select(self, change: CallbackDict[int]) -> None:
        """Handle process selection from dropdown."""
        if trial := change.get("new"):
            self.pk_input.value = trial
            self._on_load_click()

    def _on_load_click(self, _button: ipw.Button | None = None) -> None:
        """Load and display results for the given PK."""
        with self.logspace:
            self.logspace.clear_output()

            pk = self.pk_input.value
            if pk <= 0:
                self.status.failure(f"Invalid PK ({pk}), Please enter a valid process PK")
                return

            # Load the calculation node
            node = orm.load_node(pk)
            self.node_tree.value = node.uuid

            # Check if calculation finished successfully
            if node.exit_status != 0:
                self.status.failure(f"Calculation exited with status: {node.exit_status}")
                return

            # Get outputs
            if "results_dict" not in node.outputs:
                self.status.failure("No results available")
                return

            self.status.success(f"Loaded results for PK {pk}")
