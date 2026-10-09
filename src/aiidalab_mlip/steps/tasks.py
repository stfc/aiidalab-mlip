"""Select tasks widget."""

import random
from operator import not_

import ase.optimize
import ipywidgets as ipw
from alc_aiidalab_widgets.layouts import ParameterStep, WizardStep
from alc_aiidalab_widgets.types import CallbackDict
from alc_aiidalab_widgets.widgets.checkbutton import CheckButton
from alc_aiidalab_widgets.widgets.multiselect import MultiSelect
from alc_aiidalab_widgets.widgets.optional import Optional
from traitlets import dlink, link

from aiidalab_mlip.models.task import TaskModel
from aiidalab_mlip.util import tab_from_dict


class TaskWizardStep(WizardStep):
    """Wizard step for task selection."""

    def __init__(self, model: TaskModel, **kwargs) -> None:

        self.model = model

        self.spe = SPETask()
        self.geom = GeomOptTask()
        self.md = MDTask()

        self.tabs = tab_from_dict(
            ipw.Tab,
            {
                "Single Point": self.spe,
                "Geometry Optimise": self.geom,
                "Molecular Dynamics": self.md,
            },
        )

        super().__init__(
            title="Select task",
            info="Choose and configure a task from the tabs below.",
            widgets=[self.tabs],
            **kwargs,
        )
        self.ok()

    def submit(self, b) -> None:
        self.running()
        self.model.task = self.tabs.get_title(self.tabs.selected_index)
        self.model.task_parameters = self.tabs.children[self.tabs.selected_index].get()
        self.model.submitted = True
        self.ok("Parameters submitted.")
        super().submit(b)


class SPETask(ParameterStep):
    def __init__(self) -> None:
        self.properties_widget = MultiSelect(
            options=["energy", "forces", "stress", "hessian"],
            description="Properties",
        )

        super().__init__(
            title="Single point",
            info="Single point energy calculation",
            widgets={"properties": self.properties_widget},
            default_args={
                "normal": {"properties": ("energy", "forces")},
                "minimal": {"properties": ("energy",)},
                "full": {"properties": ("energy", "forces", "stress", "hessian")},
            },
            submittable=False,
        )


class GeomOptTask(ParameterStep):
    def __init__(self, **kwargs) -> None:
        widgets = {
            "optimiser": ipw.ToggleButtons(
                options=ase.optimize.__all__,
                description="Optimiser:",
                help="Name of ASE optimizer function to use.",
            ),
            "opt_cell_fully": CheckButton(
                value=True,
                description="opt_cell_fully",
                icon="check",
                help="Fully optimize the cell vectors, angles, and atomic positions.",
            ),
            "opt_cell_lengths": CheckButton(
                value=True,
                description="opt_cell_lengths",
                icon="check",
                help="Optimize cell vectors, as well as atomic positions.",
            ),
            "fmax": ipw.FloatText(
                description="fmax (eV/Å):",
                help="Maximum force for convergence, in eV/Å.",
            ),
            "steps": ipw.IntText(
                description="steps:",
                help="Maximum number of optimization steps.",
            ),
            "pressure": ipw.FloatText(
                description="Pressure (GPa):",
                help="Scalar pressure when optimizing cell geometry, in GPa.",
            ),
            "symmetrize": CheckButton(
                description="Symmetrize",
                help="Whether to refine symmetry after geometry optimization.",
            ),
            "symmetry_tolerance": ipw.FloatText(
                description="Symmetry tolerance:",
                help="Atom displacement tolerance for spglib symmetry determination, in Å.",
            ),
        }

        defaults = {
            "normal": {
                "optimiser": "BFGS",
                "opt_cell_fully": True,
                "opt_cell_lengths": True,
                "fmax": 0.01,
                "steps": 1000,
                "pressure": 0.0,
                "symmetrize": False,
                "symmetry_tolerance": 0.01,
            }
        }

        super().__init__(
            title="Geometry Optimisation",
            info="Optimise geometry of structure.",
            widgets=widgets,
            default_args=defaults,
            structure=(
                widgets["optimiser"],
                ipw.HBox((widgets["opt_cell_fully"], widgets["opt_cell_lengths"])),
                widgets["fmax"],
                widgets["steps"],
                widgets["pressure"],
                ipw.HBox((widgets["symmetrize"], widgets["symmetry_tolerance"])),
            ),
            submittable=False,
            **kwargs,
        )
        widgets["opt_cell_fully"].observe(self._sync_optimiser_buttons, "value")
        dlink((widgets["symmetrize"], "value"), (widgets["symmetry_tolerance"], "disabled"), not_)

    def _sync_optimiser_buttons(self, change: CallbackDict[bool]):
        with self.logspace:
            if not change["new"]:
                self.widgets_map["opt_cell_lengths"].disabled = False
                return
            self.widgets_map["opt_cell_lengths"].value = change["new"]
            self.widgets_map["opt_cell_lengths"].disabled = True


class MDTask(ParameterStep):
    def __init__(self, **kwargs) -> None:

        widgets = {
            "steps": ipw.IntText(
                description="Steps:",
                help="Number of steps in MD simulation.",
            ),
            "timestep": ipw.FloatText(
                description="Timestep:", help="Timestep for integrator, in fs."
            ),
            # "plumed_input": ipw.FileUpload(
            #     description="Plumed file", help="Path to PLUMED input file."
            # ),
            "seed": ipw.IntText(
                value=random.getrandbits(32),
                description="Seed:",
                help="Random seed for numpy.random and random functions.",
            ),
            # Equilibration
            "equil_steps": ipw.IntText(
                description="Equilibration steps",
                help="Maximum number of steps at which to perform optimization and reset",
            ),
            "minimize_every": Optional(
                ipw.IntText(
                    description="Minimize every:",
                    help=(
                        """
                    Frequency of minimizations. Default disables minimization after
                    beginning dynamics.
                    """
                    ),
                ),
                msg="Don't minimize",
            ),
            "rescale_every": Optional(
                ipw.IntText(
                    description="Rescale every",
                    help="Frequency to rescale velocities during equilibration.",
                ),
                msg="No rescale velocities",
            ),
            "remove_rot": CheckButton(
                description="Remove rotation",
                help="Whether to remove rotation during equilibration.",
            ),
            # Ensemble configuration
            "ensemble": ipw.ToggleButtons(
                options=(
                    "nve",
                    "nvt",
                    "nvt-nh",
                    "nvt-csvr",
                    "nph",
                    "npt",
                    "npt-mtk",
                    "npt-mtk-iso",
                    "npt-mtk-aniso",
                ),
                value="nvt",
                description="Ensemble:",
                help="Name of thermodynamic ensemble.",
            ),
            "temp": ipw.FloatText(
                value=300.0, description="Temperature:", help="Temperature, in K."
            ),
            "thermostat_time": ipw.FloatText(
                value=50,
                description="Thermostat coupling (fs):",
                help=(
                    """
                    Thermostat time for NPT, NPT-MTK or NVT Nosé-Hoover simulation,
                    in fs. Default is 50 fs for NPT and NVT Nosé-Hoover, or 100 fs for
                    NPT-MTK.
                    """
                ),
            ),
            "barostat_time": ipw.FloatText(
                description="Barostat coupling (fs):",
                help=(
                    """
                    Barostat time for NPT, NPT-MTK or NPH simulation, in fs.
                    Default is 75 fs for NPT and NPH, or 1000 fs for NPT-MTK.
                    """
                ),
            ),
            "bulk_modulus": ipw.FloatText(
                description="Bulk modulus (GPa):",
                help="Bulk modulus for NPT or NPH simulation, in GPa.",
            ),
            "pressure": ipw.FloatText(
                description="Pressure (GPa):",
                help="Pressure for NPT or NPH simulation, in GPa.",
            ),
            "friction": ipw.FloatText(
                description="Friction (fs^-1):",
                help="Friction coefficient for NVT simulation, in fs^-1.",
            ),
            "taut": ipw.FloatText(
                description="Taut:",
                help="Temperature coupling time constant for NVT CSVR simulation, in fs.",
            ),
            "thermostat_chain": ipw.IntText(
                value=3,
                description="Thermostat chain length:",
                help="Number of variables in thermostat chain for NPT/NVT MTK simulation.",
            ),
            "barostat_chain": ipw.IntText(
                value=3,
                description="Barostat chain length:",
                help="Number of variables in barostat chain for NPT MTK simulation.",
            ),
            "thermostat_substeps": ipw.IntText(
                description="Thermostat substeps:",
                help="Number of sub-steps in thermostat integration for NPT/NVT MTK simulation.",
            ),
            "barostat_substeps": ipw.IntText(
                description="Barostat substeps:",
                help="Number of sub-steps in barostat integration for NPT MTK simulation.",
            ),
            # "Heating"/cooling ramp
            "temp_start": Optional(
                ipw.FloatText(description="Start temperature:"),
                help="Temperature to start heating, in K.",
                initial_value=None,
            ),
            "temp_end": Optional(
                ipw.FloatText(description="Final temperature:"),
                help="Maximum temperature for heating, in K.",
                initial_value=None,
            ),
            "temp_step": Optional(
                ipw.FloatText(description="Temperature step:"),
                help="Size of temperature steps when heating, in K.",
                initial_value=None,
            ),
            "temp_time": Optional(
                ipw.FloatText(description="Temperature time:"),
                help="Time between heating steps, in fs.",
                initial_value=None,
            ),
        }

        self.equil_opts = ipw.VBox(
            [
                widgets[prop]
                for prop in (
                    "equil_steps",
                    "minimize_every",
                    "rescale_every",
                    "remove_rot",
                )
            ]
        )

        self.ensemble_opts = ipw.VBox(
            [
                widgets["ensemble"],
                ipw.HBox(
                    [
                        ipw.VBox(
                            [
                                widgets[prop]
                                for prop in (
                                    "temp",
                                    "thermostat_time",
                                    "friction",
                                    "taut",
                                    "thermostat_chain",
                                    "thermostat_substeps",
                                )
                            ]
                        ),
                        ipw.VBox(
                            [
                                widgets[prop]
                                for prop in (
                                    "barostat_time",
                                    "bulk_modulus",
                                    "pressure",
                                    "barostat_chain",
                                    "barostat_substeps",
                                )
                            ]
                        ),
                    ]
                ),
            ]
        )

        self.temp_ramp_opts = ipw.VBox(
            [
                widgets[prop]
                for prop in (
                    "temp_start",
                    "temp_end",
                    "temp_step",
                    "temp_time",
                )
            ]
        )

        for prop in (
            "temp_end",
            "temp_step",
            "temp_time",
        ):
            link((widgets["temp_start"]._option, "value"), (widgets[prop]._option, "value"))

        tabs = {
            "Ensemble": self.ensemble_opts,
            "Equilibration": self.equil_opts,
            "Temperature Ramping": self.temp_ramp_opts,
        }
        params_blk = tab_from_dict(ipw.Accordion, tabs)
        params_blk.selected_index = None

        super().__init__(
            title="Molecular Dynamics",
            info="Run a dynamics calculation.",
            widgets=widgets,
            default_args={"": {}},
            exclude_from_defaults=widgets.keys(),
            structure=(
                ipw.HBox([widgets["steps"], widgets["timestep"]]),
                widgets["seed"],
                params_blk,
            ),
            submittable=False,
            **kwargs,
        )

        widgets["ensemble"].observe(self._manage_ensemble, "value")
        widgets["ensemble"].value = "nve"

    def _manage_ensemble(self, value: CallbackDict[str]) -> None:
        ensemble = value["new"]

        for opt in (
            "temp",
            "thermostat_time",
            "friction",
            "taut",
            "thermostat_chain",
            "thermostat_substeps",
            "barostat_time",
            "bulk_modulus",
            "pressure",
            "barostat_chain",
            "barostat_substeps",
        ):
            self.widgets_map[opt].layout.visibility = "hidden"

        tt = self.widgets_map["thermostat_time"]
        bt = self.widgets_map["barostat_time"]

        match ensemble:
            case "nve":
                ...
            case "nvt":
                self.widgets_map["temp"].layout.visibility = "visible"
                self.widgets_map["friction"].layout.visibility = "visible"
            case "nvt-nh":
                self.widgets_map["temp"].layout.visibility = "visible"
                tt.layout.visibility = "visible"
                if tt.value == 100:
                    tt.value = 50

            case "nvt-mtk":
                self.widgets_map["temp"].layout.visibility = "visible"
                self.widgets_map["thermostat_time"].layout.visibility = "visible"
                self.widgets_map["thermostat_chain"].layout.visibility = "visible"
                self.widgets_map["thermostat_substeps"].layout.visibility = "visible"
                if tt.value == 50:
                    tt.value = 100

            case "nvt-csvr":
                self.widgets_map["temp"].layout.visibility = "visible"
                self.widgets_map["thermostat_time"].layout.visibility = "visible"
                self.widgets_map["taut"].layout.visibility = "visible"

            case "nph":
                self.widgets_map["barostat_time"].layout.visibility = "visible"
                self.widgets_map["bulk_modulus"].layout.visibility = "visible"
                self.widgets_map["pressure"].layout.visibility = "visible"

            case "npt":
                self.widgets_map["temp"].layout.visibility = "visible"
                self.widgets_map["friction"].layout.visibility = "visible"
                self.widgets_map["barostat_time"].layout.visibility = "visible"
                self.widgets_map["bulk_modulus"].layout.visibility = "visible"
                self.widgets_map["pressure"].layout.visibility = "visible"

            case "npt-mtk" | "npt-mtk-iso" | "npt-mtk-aniso":
                self.widgets_map["temp"].layout.visibility = "visible"
                self.widgets_map["thermostat_time"].layout.visibility = "visible"
                self.widgets_map["barostat_time"].layout.visibility = "visible"
                self.widgets_map["bulk_modulus"].layout.visibility = "visible"
                self.widgets_map["pressure"].layout.visibility = "visible"
                self.widgets_map["barostat_chain"].layout.visibility = "visible"
                self.widgets_map["barostat_substeps"].layout.visibility = "visible"

                if tt.value == 50:
                    tt.value = 100
