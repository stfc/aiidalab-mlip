"""Model for MLIP training step."""

from traitlets import Dict, List

from aiidalab_mlip.models import CodeModel

from .base import Model


class TrainingModel(Model):
    """Model for MLIP training step."""

    code = CodeModel()
    structures = Dict()
    training_data = List(default_value=[])
    parameters: Dict()
