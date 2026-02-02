"""Application data model for the MLIP app."""

import traitlets


class MainAppModel(traitlets.HasTraits):
    """Main application data model."""

    def __init__(self):
        """Initialize the main app model."""
        super().__init__()
        self.structure_model = StructureModel()
        self.training_model = TrainingModel()
        self.prediction_model = PredictionModel()
        self.results_model = ResultsModel()


class StructureModel(traitlets.HasTraits):
    """Model for structure selection step."""

    structure = traitlets.Instance(klass=object, allow_none=True)
    filename = traitlets.Unicode(default_value="")


class TrainingModel(traitlets.HasTraits):
    """Model for MLIP training step."""

    model_type = traitlets.Unicode(default_value="MACE")
    training_data = traitlets.List(default_value=[])


class PredictionModel(traitlets.HasTraits):
    """Model for running predictions."""

    calculation_type = traitlets.Unicode(default_value="geometry_opt")


class ResultsModel(traitlets.HasTraits):
    """Model for results viewing."""

    selected_calculation = traitlets.Instance(klass=object, allow_none=True)
    calculation_pk = traitlets.Int(default_value=0)
