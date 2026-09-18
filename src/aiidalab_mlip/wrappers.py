"""Useful decorators."""

from collections.abc import Callable, Generator
from contextlib import contextmanager
from functools import wraps
from traceback import format_exc
from typing import Concatenate, ParamSpec, TypeVar

from alc_aiidalab_widgets.types import HasStatus

P = ParamSpec("P")
T = TypeVar("T")


def handle_errors(
    func: Callable[Concatenate[HasStatus, P], T],
) -> Callable[Concatenate[HasStatus, P], T | None]:

    @wraps(func)
    def inner(self: HasStatus, *args: P.args, **kwargs: P.kwargs) -> T | None:
        with err_handler(self, func.__name__):
            return func(self, *args, **kwargs)

    return inner


@contextmanager
def err_handler(own: HasStatus, act: str) -> Generator[None, None, None]:
    """Handle error, writing to message buffer."""
    try:
        yield
    except Exception as err:
        own.status.failure(f"✗ Error in {act}: {format_exc(err)}")
