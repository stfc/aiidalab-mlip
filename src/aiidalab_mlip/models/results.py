"""Model for results viewing."""

from traitlets import Instance, Int

from .base import Model


class ResultsModel(Model):
    """Model for results viewing."""

    selected_calculation = Instance(klass=object, allow_none=True)
    calculation_pk = Int(default_value=0)
