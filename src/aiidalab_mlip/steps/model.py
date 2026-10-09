"""Results viewing wizard step."""

from pathlib import Path

import aiidalab_widgets_base as awb
import ipywidgets as ipw
from aiida import orm
from aiida.orm import Code, QueryBuilder
from aiida_mlip.data.model import ModelData
from alc_aiidalab_widgets.layouts import WizardStep
from alc_aiidalab_widgets.widgets import AiiDADatabaseQueryWidget
from alc_aiidalab_widgets.widgets.parameters import ParametersBlock
from traitlets import link

from aiidalab_mlip.models.code import CodeModel
from aiidalab_mlip.util import tab_from_dict


class ModelWizardStep(WizardStep):
    """Wizard step for viewing results."""

    def __init__(self, model: CodeModel, **kwargs):
        """
        Initialize results wizard step.

        Parameters
        ----------
        model : CodeModel
            Code
        """
        self.model = model

        self.code = ipw.Combobox(
            description="Code:",
            layout={"width": "60%"},
        )
        self.refresh_codes_button = ipw.Button(
            description="Refresh",
            button_style="info",
            tooltip="Refresh the list of available codes",
            icon="refresh",
            layout={"width": "20%"},
        )
        self.refresh_codes_button.on_click(self.update_codes)
        self.code_box = ipw.HBox(
            layout={"width": "100%"}, children=[self.code, self.refresh_codes_button]
        )
        self.update_codes()

        self.ncpus_input = ipw.BoundedIntText(
            value=self.model.ncpus,
            min=1,
            max=1024,
            step=1,
            description="No. CPUs:",
            layout=ipw.Layout(width="80%"),
        )
        link((self.ncpus_input, "value"), (self.model, "ncpus"))

        self.model_from_uri = ipw.Text(
            value="",
            description="Model:",
            placeholder="file:///Path/To/Model",
            layout=ipw.Layout(width="80%"),
        )
        self.model_from_str = ipw.Text(
            value="",
            description="Str:",
            placeholder="model",
            layout=ipw.Layout(width="80%"),
        )
        self.model_from_node = AiiDADatabaseQueryWidget(
            title="AiiDA Database",
            query=[ModelData],
        )
        self.refresh_models_button = ipw.Button(
            description="Refresh",
            button_style="info",
            tooltip="Refresh the list of available models",
            icon="refresh",
            layout={"width": "20%"},
        )
        self.refresh_models_button.on_click(self.update_models)

        self.model_node_box = ipw.HBox(
            [self.model_from_node, self.refresh_models_button], layout={"width": "100%"}
        )

        self.arch = ipw.Dropdown(
            options=(
                "mace",
                "mace_mp",
                "mace_off",
                "chgnet",
                "sevennet",
                "nequip",
                "dpa3",
                "orb",
                "mattersim",
                "grace",
                "upet",
                "fairchem",
                "mace_omol",
            ),
            description="Arch:",
            layout=ipw.Layout(width="80%"),
        )
        node_vbox = ipw.VBox([self.model_node_box, self.arch], layout={"width": "100%"})

        uri_vbox = ipw.VBox([self.model_from_uri, self.arch], layout={"width": "100%"})
        parameters_block = ParametersBlock(
            "",
            {"model": self.model_from_uri, "arch": self.arch},
            {
                "mace_mp": {
                    "model": "https://github.com/stfc/janus-core/raw/main/tests/models/mace_mp_small.model",
                    "arch": "mace_mp",
                }
            },
        )
        uri_vbox = ipw.HBox([uri_vbox, parameters_block])

        ### Str approach not supported by aiida-mlip
        # str_vbox = ipw.VBox([self.model_from_str, self.arch], layout={"width": "100%"})
        # parameters_block_str = ParametersBlock(
        #     "",
        #     {"model": self.model_from_str, "arch": self.arch},
        #     {
        #         "mace_mp": {
        #             "model": "small",
        #             "arch": "mace_mp",
        #         },
        #         "mace_off": {
        #             "model": "small",
        #             "arch": "mace_off",
        #         },
        #         "mace_omol": {
        #             "model": "extra_large",
        #             "arch": "mace_omol",
        #         },
        #         "mace_polar": {
        #             "model": "polar-1-m",
        #             "arch": "mace_polar",
        #         },
        #         "sevennet": {
        #             "model": "SevenNet-0_11July2024",
        #             "arch": "sevennet",
        #         },
        #         "orb": {
        #             "model": "orb_v3_conservative_20_omat",
        #             "arch": "orb",
        #         },
        #         "mattersim": {
        #             "model": "mattersim-v1.0.0-5M",
        #             "arch": "mattersim",
        #         },
        #         "grace": {
        #             "model": "GRACE-2L-OMAT",
        #             "arch": "grace",
        #         },
        #         "upet": {
        #             "model": "pet-mad-s",
        #             "arch": "upet",
        #         },
        #         "fairchem": {
        #             "model": "uma-m-1p1",
        #             "arch": "fairchem",
        #         },
        #     },
        # )
        # str_vbox = ipw.HBox([str_vbox, parameters_block_str])

        self.model_type = tab_from_dict(
            ipw.Tab,
            {
                # "From str": str_vbox,
                "From URI": uri_vbox,
                "AiiDA Database": node_vbox,
            },
        )

        self.device = ipw.Dropdown(
            options=("cpu", "cuda", "mps", "xpu"),
            description="Device:",
            layout=ipw.Layout(width="80%"),
        )

        info = """
            Configure the computational resources required to run the
            calculation. Additionally, you can provide a label and description for
            the AiiDA process that will be created.
        """

        super().__init__(
            title="Select Model and Code",
            info=info,
            widgets=[
                self.model_type,
                self.code_box,
                self.ncpus_input,
                self.device,
            ],
            **kwargs,
        )
        self.ok()

    def _try_load_code(self, code: str) -> Code | None:
        # Load the code
        self.running()
        self.logspace.append_stdout("Loading janus code...\n")
        try:
            return orm.load_code(code)
        except Exception:
            self.fail(f"""\
Error: Code '{code}' not found. \n
Try: verdi code create core.code.installed --config janus.yml""")

    def _load_from_str(self, model_str: str, arch: str) -> str | None: ...

    def _load_from_uri(self, model_str: str, arch: str) -> ModelData | None:
        if model_str.startswith(("http", "ftp", "sftp")):
            model_uri = model_str
            self.logspace.append_stdout("Loading model from web...")
        else:
            model_pth = Path(model_str).absolute()
            self.logspace.append_stdout("Loading model from file...")

            if not model_pth.is_file():
                self.fail(f"File ({model_str}) not found.")
                return None

            model_uri = model_pth.as_uri()

        try:
            model_str = ModelData.from_uri(model_uri, architecture=arch, cache_dir="mlips")
            model_str.label = f"{arch}:{model_uri}"
            self.model.arch = arch
            self.ok(f"Loaded model from {model_uri}.")
            return model_str
        except Exception as err:
            self.fail(f"Unable to load model from {model_uri}. \nDue to: {err}")

    def _load_from_node(self, node: ModelData, arch: str) -> ModelData | None:
        self.model.arch = arch
        return node

    def _try_load_model(self, arch: str) -> ModelData | None:

        typ = self.model_type._titles[str(self.model_type.selected_index)]

        match typ:
            case "From URI":
                return self._load_from_uri(self.model_from_uri.value, arch)
            case "AiiDA Database":
                return self._load_from_node(self.model_from_node.data_object, arch)

    def submit(self, _: ipw.Button | None = None):
        self.status.clear()
        self.logspace.clear_output()

        with self.logspace:
            self.running()
            if not (loaded_code := self._try_load_code(self.code.value)):
                return
            if not (loaded_model := self._try_load_model(self.arch.value)):
                return

            self.model.code = loaded_code
            self.model.model = loaded_model
            self.model.device = self.device.value
            self.model.submitted = True
            self.ok(f"Loaded code: {loaded_code}, model: {loaded_model}")

        super().submit(_)

    def update_codes(self, _: ipw.Button | None = None) -> None:
        """Update the list of available codes."""
        qb = QueryBuilder()
        qb.append(Code, project=["label", "id"])

        codes = qb.all()
        code_labels = [f"{label}" for label, _ in codes]
        self.code.options = code_labels

        if code_labels:
            self.code.value = code_labels[0]

    def update_models(self, _: ipw.Button | None = None) -> None:
        """Update the list of available models."""
        qb = QueryBuilder()
        qb.append(ModelData, project=["label", "id"])

        models = qb.all()
        model_labels = [(f"{label or repr(label)}:{idx}", idx) for label, idx in models]
        self.model_from_node.options = model_labels

        if model_labels:
            self.model_from_node.value = model_labels[0]
