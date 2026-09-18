"""Main application data model."""


from traitlets import HasTraits, Unicode

from . import CodeModel, PredictionModel, ResultsModel, StructureModel, TaskModel


class MainAppModel(HasTraits):
    """Main application data model."""

    process_label = Unicode("")
    process_description = Unicode("")

    def __init__(self) -> None:
        """Initialize the main app model."""
        super().__init__()
        self.structure_model = StructureModel()
        self.mlip_model = CodeModel()
        self.task_model = TaskModel()
        self.prediction_model = PredictionModel()
        self.results_model = ResultsModel()
