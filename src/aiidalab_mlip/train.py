"""Defines the main AiiDAlab MLIP training page."""

from datetime import datetime

import aiidalab_widgets_base as awb
import ipywidgets as ipw
from IPython.display import display

from aiidalab_mlip.models import TrainingModel
from aiidalab_mlip.steps import (
    DistributeWizardStep,
    ModelWizardStep,
    MultiStructureStep,
    ResultsWizardStep,
    RunWizardStep,
)


class TrainApp:
    """The main AiiDAlab MLIP application class."""

    def __init__(self) -> None:
        """MainApp constructor."""
        self.model = TrainingModel()
        self.view = TrainAppView(self.model)
        display(self.view)


class TrainAppView(ipw.VBox):
    """Training app."""

    def __init__(self, model: TrainingModel, **kwargs) -> None:
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
                Train and deploy ML potentials for molecular simulations
            </h2>
            """
        )

        header = ipw.VBox(
            children=[
                logo,
                subtitle,
            ],
            layout={"margin": "auto"},
        )

        footer = ipw.HTML(
            f"""
            <footer style="text-align: center; margin-top: 20px;">
                Copyright (c) {datetime.now().year} MLIP Development Team
            </footer>
            """,
        )

        self.main = TrainWizardWidget(model)

        super().__init__(layout={}, children=[header, self.main, footer], **kwargs)


class TrainWizardWidget(ipw.VBox):
    """Widget to hold the main MLIP training application wizard."""

    def __init__(self, model: TrainingModel, **kwargs) -> None:
        """
        WizardWidget constructor.

        Parameters
        ----------
        model : MainAppModel
            The application data model
        **kwargs :
            Keyword arguments passed to ipywidgets.VBox.__init__()
        """
        self.structure_step = MultiStructureStep(model)
        self.model_step = ModelWizardStep(model.code)
        self.distribute_step = DistributeWizardStep(model)
        # self.task_step = TaskWizardStep(model.task_model)
        self.run_step = RunWizardStep(model)
        # self.results_step = ResultsWizardStep(model.results_model)

        # Link structure to prediction step
        # def update_prediction_structure(change: dict[str, Atoms]) -> None:
        #     self.prediction_step._parent_structure = change["new"]

        # model.structure_model.observe(update_prediction_structure, names="structure")

        self._wizard_app_widget = awb.WizardAppWidget(
            steps=[
                ("Select Structure", self.structure_step),
                ("Select model", self.model_step),
                ("Distribute data", self.distribute_step),
                # ("Train MLIP", self.training_step),
                ("Run", self.run_step),
                # ("View Results", self.results_step),
            ],
        )

        super().__init__(
            children=[self._wizard_app_widget],
            **kwargs,
        )
