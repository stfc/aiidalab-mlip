"""Defines the data distribution step."""
from collections.abc import Generator

import ipywidgets as ipw
from aiida_mlip.calculations.descriptors import Descriptors
from alc_aiidalab_widgets.layouts import WizardStep
from plotly.graph_objects import FigureWidget


class DistributeWizardStep(WizardStep):
    """Wizard step for data distribution."""

    FACTORS = ("Train", "Test", "Validation")
    DEFAULTS = {"Train": 0.6, "Test": 0.3, "Validation": 0.1}

    def __init__(self, model, **kwargs):
        self.ratio = {}
        self.labels = {}
        cont = []
        for i in self.FACTORS:
            self.ratio[i] = ipw.FloatSlider(
                min=0.0,
                max=1.0,
                value=self.DEFAULTS[i],
                readout=False,
                description=i + ":",
                layout={"width": "80%", "margin": "auto"},
            )
            self.labels[i] = ipw.Label(layout={"width": "20%", "margin": "auto"})
            cont.append(
                ipw.HBox([self.ratio[i], self.labels[i]], layout={"width": "30%", "margin": "auto"})
            )
            self.ratio[i].observe(self._update_ratio, "value")

        ratios = ipw.HBox(cont)
        self.plot = FigureWidget()
        self.compute = ipw.Button("Calculate descriptors")
        self.compute.observe(self._compute_descriptors)

        super().__init__(
            title="Run Predictions",
            info="Run calculations using the trained MLIP model.",
            widgets=[ratios, self.plot, self.compute],
            **kwargs,
        )
        self._update_ratio()

    @property
    def values(self) -> Generator[float]:
        return (x.value for x in self.ratio.values())

    def _update_ratio(self, *_) -> None:
        total = sum(self.values)

        for factor in self.FACTORS:
            self.labels[factor].value = f"{self.ratio[factor].value / total:4.2%}"

    def _compute_descriptors(self, *_):
        Descriptors
