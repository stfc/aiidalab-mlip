"""Base model from which other models are derived."""

from traitlets import HasTraits, Bool


class Model(HasTraits):
    """Base model from which other models are derived."""

    submitted = Bool()
