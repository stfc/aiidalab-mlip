"""Node displays in node tree."""

import re
import traceback
from typing import Any, TypeVar

import ipywidgets as ipw
import numpy as np
import yaml
from aiida.common import NotExistentAttributeError
from aiida.orm import (
    Dict,
    Node,
    ProcessNode,
    SinglefileData,
    StructureData,
    TrajectoryData,
)
from aiidalab_widgets_base.loaders import LoadingWidget
from aiidalab_widgets_base.viewers import AIIDA_VIEWER_MAPPING, DictViewer
from alc_aiidalab_widgets.types import CallbackDict
from alc_aiidalab_widgets.widgets import Status, StructureViewWidget
from alc_aiidalab_widgets.widgets.extxyz_stats import ExtXYZStatsViewer
from alc_aiidalab_widgets.widgets.tables import GenericArrayDataTableWidget
from alc_aiidalab_widgets.widgets.vib_modes import VibrationalModesViewWidget
from ase import Atoms
from IPython.display import display
from traitlets import Instance, observe

T = TypeVar("T")


class SummaryViewer(ipw.VBox):
    """View summary of job node."""

    def __init__(self, node: ProcessNode, **kwargs) -> None:

        textbox = ipw.HTML()
        children = [textbox]

        text = []
        text.append(
            f"""\
=== Calculation Results ===
Type: {node.process_label}
State: {node.process_state.value}
            """
        )

        if node.process_state.value in {"finished", "excepted", "killed"}:
            text.append(
                f"""\
Exit status: {node.exit_status}
Created: {node.ctime}
Finished: {node.mtime}
                """
            )

        try:
            results = node.outputs.results_dict.get_dict()
        except NotExistentAttributeError:
            textbox.value = "<br>".join(text).replace("\n", "<br>")
            super().__init__(children=children, **kwargs)
            return

        # Display energy
        if (energy := self._get_dict_ci(results.get("info", {}), "energy")) is not None:
            text.append(f"Energy: {energy:.6f} eV")

        # Display forces info
        if (forces := self._get_dict_ci(results, "force")) is not None:
            force_magnitudes = np.linalg.norm(forces, axis=1)
            text.append(
                f"""\
Forces:
   Max: {force_magnitudes.max():.4f} eV/Å
   Mean: {force_magnitudes.mean():.4f} eV/Å
   RMS: {np.sqrt((force_magnitudes**2).mean()):.4f} eV/Å
"""
            )

        if (stress := self._get_dict_ci(results.get("info", {}), "stress")) is not None:
            text.append(f"Stress tensor: {stress}\n")

        if "positions" in results and "numbers" in results:
            # Display structure info
            n_atoms = len(results["positions"])
            elements = set(results["numbers"])
            text.append(
                f"""\
Structure:
   Atoms: {n_atoms}
   Elements: {", ".join(map(str, sorted(elements)))}
   PBC: {results.get("pbc", "N/A")}
"""
            )

            # Try to visualize structure
            try:
                text.append("Structure Visualization:")
                atoms = Atoms(
                    numbers=results["numbers"],
                    positions=results["positions"],
                    cell=results.get("cell"),
                    pbc=results.get("pbc", [True, True, True]),
                )
                view = StructureViewWidget(atoms)
                display(view)
            except Exception as e:
                print(f"Warning: Could not display structure: {e}")

            children.append(view)

        textbox.value = "<br>".join(text).replace("\n", "<br>")

        super().__init__(children=children, **kwargs)

    @staticmethod
    def _get_dict_ci(d: dict[str, T], key: str) -> T | None:
        """Get from dict fuzzily and case insensitively."""
        return next((d[dkey] for dkey in d if key in dkey.lower()), None)


AIIDA_VIEWER_MAPPING.update(
    {
        "aiida.calculations:mlip.sp": SummaryViewer,
        "aiida.calculations:mlip.md": SummaryViewer,
        "aiida.calculations:mlip.opt": SummaryViewer,
        "aiida.calculations:mlip.ph": SummaryViewer,
    }
)


class CustomAiidaNodeViewWidget(ipw.VBox):
    """
    Custom viewer based on a specific AiiDA node type.

    An extension of the aiida_widgets_base.viewers.AiidaNodeViewWidget
    enabling more customisability when registering viewers with nodes
    returned from ChemShell jobs. The main outline is taken from the base
    aiidalab_widgets_base viewer with an extended viewer() method which
    allows handling of node types which the base viewer has no registered
    visualisation widgets.
    """

    node = Instance(Node, allow_none=True)

    def __init__(self, **kwargs):
        """CustomAiidaNodeViewWidget Constructor."""
        self._output = ipw.Output()
        self.node_views = {}
        self.node_view_loading_message = LoadingWidget("Loading Node View")
        super().__init__(**kwargs)
        self.add_class("aiida-node-view-widget")

    @observe("node")
    def _observe_node(self, change: CallbackDict[Node]):
        if not ((node := change["new"]) and node != change["old"]):
            return

        if node.uuid in self.node_views:
            self.children = [self.node_views[node.uuid]]
            return

        self.children = [self.node_view_loading_message]
        try:
            node_view = self._viewer(node)
        except Exception as err:
            node_view = Status()
            node_view.failure("\n".join(traceback.format_exception(err)))

        if isinstance(node_view, ipw.DOMWidget):
            self.node_views[node.uuid] = node_view
            self.children = [node_view]
        else:
            with self._output:
                self._output.clear_output()
                if change["new"]:
                    display(node_view)
            self.children = [self._output]

    @staticmethod
    def _viewer(node: Node, **kwargs) -> Any:
        """Create a viewer based on the type of Node being visualised."""
        viewer = AIIDA_VIEWER_MAPPING.get(node.node_type)

        match node:
            case ProcessNode():
                # Allow to register specific viewers based on node.process_type
                viewer = AIIDA_VIEWER_MAPPING.get(node.process_type, viewer)
                return viewer(node, **kwargs)
            case StructureData():
                return StructureViewWidget(node=node, **kwargs)
            case TrajectoryData():
                return StructureViewWidget(node=node, **kwargs)

            case SinglefileData(filename="aiida-stats.dat"):
                with node.open(None, "r") as file:
                    header = [
                        "_".join(re.sub(r"\W+", " ", head).strip().split())
                        for head in next(file, "").strip("#").split("|")
                    ]
                    return GenericArrayDataTableWidget.from_file(file, header)

            case SinglefileData(filename="aiida-dos.dat"):
                with node.open(None, "r") as file:
                    widget = GenericArrayDataTableWidget.from_file(file, ["Frequency", "Intensity"])
                widget.x_selector.value = "Frequency"
                widget.show_selector.value = {"Intensity"}
                widget.show_plt_btn.click()
                return widget

            case SinglefileData(filename="aiida-pdos.dat"):
                with node.open(None, "r") as file:
                    next(file)
                    data = next(file).split()
                    file.seek(0)
                    return GenericArrayDataTableWidget.from_file(
                        file,
                        header=["Frequency", *(f"Atom_{i}" for i, _ in enumerate(data[1:], 1))],
                    )

            # Don't currently handle this type of file.
            case SinglefileData(filename="aiida-force_constants.hdf5"):
                ipw.HTML(f"Cannot currently show contents of {node.filename}")

            case SinglefileData(filename="aiida-auto_bands.yml.xz"):
                return VibrationalModesViewWidget.from_phonopy_yaml(
                    node, layout=ipw.Layout(width="100%", min_height="10cm")
                )

            case SinglefileData() if node.filename.endswith((".yaml", ".yml")):
                with node.open(None, "r") as file:
                    d = yaml.safe_load(file)
                if isinstance(d.get("info"), dict):
                    d.update(d.pop("info"))
                return DictViewer(
                    Dict(d), layout=ipw.Layout(max_height="22em", overflow="scroll hidden")
                )

            case SinglefileData() if node.filename.endswith((".xyz", ".extxyz")):
                return ExtXYZStatsViewer(node=node, **kwargs)

            case SinglefileData():
                viewer = ipw.Output()
                viewer.append_stdout(node.get_content("r"))
                return viewer

            case _ if viewer:
                return viewer(node, **kwargs)

        # No viewer registered for this type, return node itself
        return node
