"""Structure selection wizard step."""

from __future__ import annotations

import io
from abc import abstractmethod
from typing import Any

import ipywidgets as ipw
from aiida.orm import Node, SinglefileData, StructureData
from aiidalab_widgets_base import SmilesWidget
from alc_aiidalab_widgets.layouts import WizardStep
from alc_aiidalab_widgets.types import CallbackDict
from alc_aiidalab_widgets.widgets.database import AiiDADatabaseQueryWidget
from alc_aiidalab_widgets.widgets.file_handling import FileUploadWidget
from alc_aiidalab_widgets.widgets.structure import StructureViewWidget
from ase import Atoms
from ase.io.formats import UnknownFileTypeError, filetype
from ase.io.formats import read as ase_read
from typing_extensions import override

from aiidalab_mlip.models import TrainingModel
from aiidalab_mlip.models.structure import StructureModel
from aiidalab_mlip.util import tab_from_dict


class StructureGetter:
    """Base class containing structure getting routines."""

    logspace: ipw.Output

    def __init__(self, *args, **kwargs) -> None:
        # upload file
        self.file_uploader = FileUploadWidget(description="Structure file: ")
        self.file_input_widget = ipw.VBox([self.file_uploader])

        self.viewer = StructureViewWidget()

        # AiiDA database
        self.database_widget = AiiDADatabaseQueryWidget(
            title="AiiDA Database",
            query=[SinglefileData, StructureData],
        )

        self.smiles_widget = SmilesWidget(title="SMILES")

        self.tabs = tab_from_dict(
            ipw.Tab,
            {
                "Upload File": self.file_input_widget,
                "AiiDA Database": self.database_widget,
                "SMILES String": self.smiles_widget,
            },
        )

        self.file_uploader.observe(self._on_file_upload, "file")
        self.database_widget.observe(self._on_database_search, "data_object")
        self.smiles_widget.observe(self._on_smiles_generation, "structure")

    @abstractmethod
    def _on_file_upload(self, _change: CallbackDict[SinglefileData], /) -> None:
        raise NotImplementedError

    @abstractmethod
    def _on_database_search(self, _change: CallbackDict[Node], /) -> None:
        raise NotImplementedError

    @abstractmethod
    def _on_smiles_generation(self, _change: CallbackDict[Atoms], /) -> None:
        raise NotImplementedError

    def _get_uploaded_structure(
        self, change: CallbackDict[SinglefileData]
    ) -> tuple[str, Atoms | list[Atoms]]:
        """When file upload button is pressed."""
        file_data = change.get("new")

        assert file_data

        try:
            file = io.StringIO(file_data.get_content("r"))
        except UnicodeDecodeError:
            file = io.BytesIO(file_data.get_content("rb"))

        try:
            format = filetype(file_data.filename, read=False)
        except UnknownFileTypeError:
            format = filetype(io.BytesIO(bytes(file.read(1000), encoding="utf-8")), read=True)
            file.seek(0)

        structure = ase_read(file, index=":", format=format)

        return file_data.filename, structure

    def _get_smiles_generation(self, change: CallbackDict[Atoms]) -> Atoms:
        """When SMILES string is inputted."""
        assert change["new"] is not None

        return change["new"]

    def _get_database(
        self, node: Node, change: CallbackDict[Node]
    ) -> tuple[str | None, Atoms | list[Atoms] | None]:
        """When data is loaded from AiiDA database."""
        match node:
            case SinglefileData():
                return self._get_uploaded_structure(change)
            case StructureData():
                structure: Atoms = node._get_object_ase()
                return None, structure
            case _:
                return None, None

    def _display_structure_info(self, structure: Atoms | None) -> None:
        """Display structure info."""
        if structure is None:
            self.viewer.viewer = None
            return

        self.viewer.assign_structure_from_ase(structure)
        with self.logspace:
            self.logspace.clear_output()
            print(f"Formula: {structure.get_chemical_formula()}")
            print(f"Number of atoms: {len(structure)}")
            print(f"Cell: {structure.get_cell()}")


class StructureWizardStep(StructureGetter, WizardStep):
    """Wizard step for structure selection."""

    def __init__(self, model: StructureModel, /, **kwargs: Any) -> None:
        """Initialize structure wizard step."""
        self.model = model

        StructureGetter.__init__(self, **kwargs)
        self.slider = ipw.IntSlider(
            description="Frame",
            disabled=True,
            layout={"width": "50%", "margin": "auto"},
        )
        self.slider.observe(self._on_slider_select, "value")
        WizardStep.__init__(
            self,
            title="Select or Upload Structure",
            info="Choose a structure.",
            widgets=(
                self.tabs,
                self.slider,
                self.viewer,
            ),
            **kwargs,
        )
        self._structures: list[Atoms] = []
        self.structures = None

    @property
    def current_structure(self) -> Atoms:
        """Current structure."""
        return self.model.structure

    @current_structure.setter
    def current_structure(self, value: Atoms | int) -> None:
        match value:
            case int():
                value = self.structures[value]
            case Atoms():
                pass

        self.model.structure = value
        self._display_structure_info(value)

    @property
    def structures(self) -> list[Atoms]:
        """List of available structures."""
        return self._structures

    @structures.setter
    def structures(self, value: list[Atoms] | Atoms | None) -> None:
        if value is None:
            self.slider.min = 0
            self.slider.max = 0
            self.slider.value = 0
            self.slider.disabled = True
            self._structures.clear()
            self._display_structure_info(None)
            return

        self._structures = [value] if isinstance(value, Atoms) else value

        self.slider.min = 0
        self.slider.max = len(self.structures) - 1
        self.slider.value = 0
        self.slider.disabled = False

    @override
    def _on_file_upload(self, change: CallbackDict[SinglefileData]) -> None:

        if not change["new"]:
            return

        self.status.clear()
        self.running()
        self.structures = None

        with self.logspace:
            self.logspace.clear_output()
            try:
                filename, self.structures = self._get_uploaded_structure(change)
            except Exception:
                self.fail(
                    f"Unable to load {change['new'].filename}."
                )

        if self.status.status is self.status._Stat.FAILURE:
            self.fail()
            return

        # Store in model
        self.model.filename = filename
        self.current_structure = 0

        # Update status
        self.ok(
            f"Loaded {filename}: "
            f"{len(self.structures)} frames, {len(self.current_structure)} atoms."
        )

    def _on_slider_select(self, new: int) -> None:
        self.current_structure = new

    @override
    def _on_smiles_generation(self, change: CallbackDict[Atoms]) -> None:
        """When SMILES string is inputted."""
        if change["new"] == change["old"]:
            return

        self.structures = self._get_smiles_generation(change)
        self.current_structure = 0

        # Update status
        self.ok(f"Loaded {self.smiles_widget.smiles.value}: {len(self.structures[0])} atoms.")

    @override
    def _on_database_search(self, change: CallbackDict[Node]) -> None:
        """When data is loaded from AiiDA database."""
        node = change.get("new")
        if not node or node == change["old"]:
            return

        self.slider.disabled = True
        filename, self.structures = self._get_database(node, change)

        if not self.structures:
            self.fail(f"Cannot load structure from {node.node_type}")
            return

        self.current_structure = 0
        self.model.filename = filename or "Unknown"
        self.ok(f"Loaded structure from {node.pk}.")

    def submit(self, b: ipw.Button) -> None:
        """Submit the structure step."""
        with self.logspace:
            if self.model.structure or self.model.filename:
                self.file_uploader.disable(True)
                self.database_widget.disable(True)
                self.model.submitted = True
                self.ok("Structure submitted.")
            else:
                self.model.submitted = False
                self.fail("No structure defined.")

            super().submit(b)


class MultiStructureStep(StructureGetter, WizardStep):
    """x."""

    def __init__(self, model: TrainingModel, /, **kwargs: Any) -> None:
        """Initialize structure wizard step."""
        self.model = model

        self.structure_list = ipw.Select(layout={"margin": "auto", "width": "80%"})
        self.structure_list.observe(self._selection_changed, "value")

        StructureGetter.__init__(self, **kwargs)
        WizardStep.__init__(
            self,
            title="Select or Upload Structure",
            info="Choose a structure.",
            widgets=(
                self.tabs,
                self.structure_list,
                self.viewer,
            ),
            **kwargs,
        )

    def _update_structures(self) -> None:
        self.structure_list.options = self.model.structures.keys()

    def _selection_changed(self, selection: CallbackDict[str]) -> None:
        self._display_structure_info(self.model.structures[selection["new"]])

    @override
    def _on_file_upload(self, change: CallbackDict[SinglefileData]) -> None:
        self.status.clear()

        self.running()

        if not change["new"]:
            return

        with self.logspace:
            self.logspace.clear_output()
            filename, structure = self._get_uploaded_structure(change)

        if self.status.status is self.status._Stat.FAILURE:
            self.ready()
            return

        # Store in model
        self.model.structures[filename] = structure

        # Update status
        self._update_structures()
        self.ok(f"Loaded {filename}: {len(structure)} atoms.")
        self.ready()

    @override
    def _on_smiles_generation(self, change: CallbackDict[Atoms]) -> None:

        if change["new"] == change["old"]:
            return

        structure = self._get_smiles_generation(change)

        self.model.structures[structure.get_chemical_formula()] = structure

        # Update status
        self._update_structures()
        self.ok(f"Loaded {self.smiles_widget.smiles.value}: {len(structure)} atoms.")
        self.ready()

    @override
    def _on_database_search(self, change: CallbackDict[Node]) -> None:
        node = change.get("new")
        if not node or node == change["old"]:
            return

        filename, structure = self._get_database(node, change)
        if structure:
            self._update_structures()
            self.model.structures[filename or str(hash(structure))] = structure
            self.ok(f"Loaded structure from {node.pk}")
        else:
            self.fail(f"Cannot load structure from {node.node_type}")

        self.ready()
