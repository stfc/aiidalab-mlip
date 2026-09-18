"""Model holding code and MLIP."""

from aiida.orm import Code
from aiida_mlip.data.model import ModelData
from traitlets import Instance, Int, Unicode

from .base import Model


class CodeModel(Model):
    """Model holding code and MLIP."""

    code = Instance(klass=Code)

    ncpus = Int(4)

    model = Instance(klass=ModelData)
    arch = Unicode()
    device = Unicode()
