"""Results viewing wizard step."""

import ipywidgets as ipw
from aiida import orm
from aiida.orm import Code, QueryBuilder
from aiida_mlip.data.model import ModelData
from alc_aiidalab_widgets.layouts import WizardStep
from alc_aiidalab_widgets.widgets.model_select import AiiDAMlipModelSelect
from traitlets import link

from aiidalab_mlip.models.code import CodeModel


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

        self.model_type = AiiDAMlipModelSelect()

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

    def _try_load_model(self) -> tuple[str, ModelData] | None:
        return self.model_type._try_load_model()

    def submit(self, _: ipw.Button | None = None):
        self.status.clear()
        self.logspace.clear_output()

        with self.logspace:
            self.running()
            if not (loaded_code := self._try_load_code(self.code.value)):
                return
            if not (loaded_model := self._try_load_model()):
                return

            self.model.code = loaded_code
            self.model.arch, self.model.model = loaded_model
            self.model.device = self.device.value
            self.model.calc_kwargs = self.model_type.calc_kwargs
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
