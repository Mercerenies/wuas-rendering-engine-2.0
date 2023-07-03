
"""Global registry of board processors. Any processor can register
itself with this registry using the @registered_processor decorator, and
processors can be queried by name from the REGISTERED_PROCESSORS
mapping."""

from __future__ import annotations

from wuas.processing.abc import BoardProcessor

from typing import Callable, Type, TypeVar, Any, overload

_T = TypeVar("_T", bound=BoardProcessor)

REGISTERED_PROCESSORS: dict[str, Callable[[], BoardProcessor]] = {}


@overload
def registered_processor(cls: Type[_T]) -> Type[_T]: ...
@overload
def registered_processor(*, aliases: list[str]) -> Callable[[Type[_T]], Type[_T]]: ...


def registered_processor(cls: Any = None, *, aliases: Any = None):
    """Decorator which registers a class as a processor. The class must
    derive from BoardProcessor and must be constructible with no
    arguments.

    The class is registered with its own fully-qualified name (including
    module). Optionally, aliases can be supplied, which will be
    available as additional names for the class.

    This decorator can be called with or without arguments. Calling the
    decorator without arguments is equivalent to calling it with
    aliases=[].

    @registered_processor
    class MyProcessor(BoardProcessor):
        ...

    @registered_processor(aliases=['myprocessor'])
    class MyProcessor(BoardProcessor):
        ...

    """
    if aliases is None:
        return registered_processor(aliases=[])(cls)

    def wrapper(cls: Any):
        REGISTERED_PROCESSORS[cls.__module__ + "." + cls.__name__] = cls
        for alias in aliases:
            REGISTERED_PROCESSORS[alias] = cls
        return cls
    return wrapper
