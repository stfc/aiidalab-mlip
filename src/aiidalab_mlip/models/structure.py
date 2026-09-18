"""Structure model."""
from ase import Atoms
from traitlets import Instance, Unicode

from .base import Model


class StructureModel(Model):
    """Model for structure selection step."""

    structure = Instance(klass=Atoms, allow_none=True)
    filename = Unicode(default_value="")
