
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
    if aliases is None:
        return registered_processor(aliases=[])(cls)

    def wrapper(cls: Any):
        REGISTERED_PROCESSORS[cls.__module__ + "." + cls.__name__] = cls
        for alias in aliases:
            REGISTERED_PROCESSORS[alias] = cls
        return cls
    return wrapper
