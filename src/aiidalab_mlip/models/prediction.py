"""Model for running predictions."""

from traitlets import Unicode

from .base import Model


class PredictionModel(Model):
    """Model for running predictions."""

    calculation_type = Unicode(default_value="geometry_opt")
