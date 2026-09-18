"""Model for task step."""
from traitlets import Bool, Dict, Unicode

from .base import Model


class TaskModel(Model):
    """Model for task step."""

    submitted: Bool(False)
    task = Unicode()
    task_parameters = Dict(key_trait=Unicode())
