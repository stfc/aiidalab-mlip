import traceback
from typing import Any, TypeVar

import ipywidgets as ipw
import numpy as np
import yaml
from aiida.orm import (
    ArrayData,
    Dict,
    Float,
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
from ase import Atoms
from IPython.display import display
from traitlets import Instance, observe

T = TypeVar("T")


class AiidaGradientDataViewWidget(ipw.VBox):
    """Custom widget to display array data produced from AiiDA-mlip jobs."""

    def __init__(self, array: ArrayData, **kwargs):
        """AiidaArrayDataViewWidget Constructor.

        Parameters
        ----------
        array : ArrayData
            The AiiDA ArrayData object to display.
        """
        super().__init__(**kwargs)
        self.array = array
        self.array_names = array.get_arraynames()

        self.array_selector = ipw.Dropdown(
            options=self.array_names,
            description="Array Label:",
            disabled=False,
            layout={"width": "30%"},
        )
        self._render_array({"new": self.array_selector.index, "old": -1})
        self.array_selector.observe(self._render_array, "index")

    def _render_array(self, change) -> None:
        """Create a HTML table based on the currently selected array."""
        index = change["new"]
        if index == change["old"]:
            return
        values = self.array.get_array(self.array_names[index])
        # Construct HTML Table
        html = "<table style='width:100%; border: 1px solid #ddd; text-align: left; "
        html += "border-collapse: collapse;'>"
        html += "<tr style='background-color: #2196F3; color: white;'>"
        html += "<th>Atom Index</th><th>X</th><th>Y</th><th>Z</th></tr>"

        for idx, row in enumerate(values):
            bg_color = "#f9f9f9" if idx % 2 == 0 else "#ffffff"
            html += f"<tr style='background-color: {bg_color};'>"
            html += f"<td><b>{idx}</b></td><td>{row[0]:.6f}</td><td>{row[1]:.6f}</td>"
            html += f"<td>{row[2]:.6f}</td>"
            html += "</tr>"
        html += "</table>"

        self.children = [self.array_selector, ipw.HTML(html)]


class VibrationalModesViewWidget(ipw.VBox):
    """Custom widget to display vibrational modes produced from ChemShell."""

    def __init__(self, array: ArrayData, **kwargs) -> None:
        """VibrationalModesViewWidget Constructor.

        Parameters
        ----------
        array : ArrayData
            The AiiDA ArrayData object to display.
        """
        super().__init__(**kwargs)
        self.array = array
        values = self.array.get_array("Modes")
        # Construct HTML Table
        html = "<table style='width:100%; border: 1px solid #ddd; text-align: left; "
        html += "border-collapse: collapse;'>"
        html += "<tr style='background-color: #2196F3; color: white;'>"
        html += "<th>Mode</th><th>Frequency</th><th>Vib T / K</th><th>ZPE / H</th>"
        html += "</th><th>Energy / H</th></th><th>-TS / H</th></tr>"

        for idx, row in enumerate(values):
            bg_color = "#f9f9f9" if idx % 2 == 0 else "#ffffff"
            html += f"<tr style='background-color: {bg_color};'>"
            html += f"<td><b>{idx}</b></td><td>{row[0]:.6f}</td><td>{row[1]:.6f}</td>"
            html += f"<td>{row[2]:.6f}</td><td>{row[3]:.6f}</td><td>{row[4]:.6f}</td>"
            html += "</tr>"
        html += "</table>"

        self.children = [ipw.HTML(html)]


class SummaryViewer(ipw.VBox):
    def __init__(self, node, **kwargs) -> None:

        results = node.outputs.results_dict.get_dict()

        textbox = ipw.HTML()
        children = [textbox]

        text = []

        text.append(
            f"""\
=== Calculation Results ===
Type: {node.process_label}
State: {node.process_state}
Exit status: {node.exit_status}
Created: {node.ctime}
Finished: {node.mtime}

"""
        )

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


class AiiDAMLIPStatsViewer(ipw.HTML):
    DEFAULT_STYLE = """
    <style>
    table, th, td { border: 1px solid black; }
    tr:nth-child(odd) { background-color: #e5e7e9; }
    tr:nth-child(odd):hover { background-color:   #f5b7b1; }
    tr:nth-child(even):hover { background-color:  #f5b7b1; }
    th, td { padding: 10px; }
    td { min-width: 100px; text-align: center; border: none }
    th { text-align: center; border: none;  border-bottom: 1px solid black;}
    </style>
    """

    def __init__(self, node: SinglefileData, **kwargs):
        super().__init__(value=DEFAULT_STYLE, **kwargs)

        with node.open(None, "r") as file:
            header = next(file, "").strip("#")

            self.value += "<table>\n<tr>\n"
            self.value += "\n".join(f"<th>{head.strip()}</th>" for head in header.split("|"))
            self.value += "\n</tr>\n"

            for line in file:
                self.value += "\n<tr>\n"
                self.value += "\n".join(f"<td>{data}</td>" for data in line.split())
                self.value += "\n</tr>\n"

            self.value += "\n</table>"


AIIDA_VIEWER_MAPPING.update(
    {
        "aiida.calculations:mlip.sp": SummaryViewer,
        "aiida.calculations:mlip.md": SummaryViewer,
        "aiida.calculations:mlip.opt": SummaryViewer,
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
            case SinglefileData() if node.filename.endswith((".yaml", ".yml")):
                with node.open(None, "r") as file:
                    d = yaml.safe_load(file)
                if isinstance(d.get("info"), dict):
                    d.update(d.pop("info"))
                return DictViewer(Dict(d))
            case SinglefileData() if node.filename.endswith(".xyz"):
                return StructureViewWidget(node=node, **kwargs)
            case SinglefileData() if node.filename == "aiida-stats.dat":
                return AiiDAMLIPStatsViewer(node=node, **kwargs)
            case SinglefileData():
                viewer = ipw.Output()
                viewer.append_stdout(node.get_content("r"))
                return viewer
            case ArrayData() if "Energy Derivative" in node.label:
                return AiidaGradientDataViewWidget(node, **kwargs)
            case ArrayData() if "Vibrational" in node.label:
                return VibrationalModesViewWidget(node, **kwargs)

            case Float() if "SCF Energy" in node.label:
                return f"Final SCF Energy (Hartree): {node.value}"

            case _ if viewer:
                return viewer(node, **kwargs)

        # No viewer registered for this type, return node itself
        return node
