
"""Helper utility for constructing global registries of particular
classes."""

from __future__ import annotations

from typing import Mapping, Callable, Iterator, overload, Any


class ClassRegistry[T](Mapping[str, Callable[[], T]]):
    _dict: dict[str, Callable[[], T]]

    def __init__(self) -> None:
        self._dict = {}

    def __getitem__(self, key: str) -> Callable[[], T]:
        return self._dict[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._dict)

    def __len__(self) -> int:
        return len(self._dict)

    def register_callable(self, name: str, func: Callable[[], T]) -> None:
        if name in self._dict:
            raise ValueError(f"Already registered: {name}")
        self._dict[name] = func

    @overload
    def register_class[S: type[T]](self, cls: S) -> S: ...
    @overload
    def register_class(self, *, aliases: list[str]) -> Callable[[type[T]], type[T]]: ...

    def register_class(self, cls: Any = None, *, aliases: Any = None) -> Any:
        """Decorator which registers a class with this registry. The
        class must derive from the registry's target type T and must
        be constructible with no arguments.

        The class is registered with its own fully-qualified name
        (including module). Optionally, aliases can be supplied, which
        will be available as additional names for the class.

        This decorator can be called with or without arguments.
        Calling the decorator without arguments is equivalent to
        calling it with aliases=[].

        @registry.register_class
        class MyClass:
            ...

        @registry.register_class(aliases=['myprocessor'])
        class MyProcessor(BoardProcessor):
            ...

        """
        if aliases is None:
            return self.register_class(aliases=[])(cls)

        def wrapper(cls: type[T]) -> type[T]:
            self.register_callable(f"{cls.__module__}.{cls.__name__}", cls)
            for alias in aliases:
                self.register_callable(alias, cls)
            return cls
        return wrapper
