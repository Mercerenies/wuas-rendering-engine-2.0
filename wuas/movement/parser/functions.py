
"""Built-in functions available in the movement language API.

For the purposes of this module, a WUAS movement Function is a
callable object which takes a Prolog Call and produces an Event,
raising a ParseError on failure.

"""

from __future__ import annotations

from typing import Callable
from attrs import define

from wuas.movement.prolog import Call
from wuas.movement.events import Event
from .assertions import assert_arity


type Function = Callable[[Call], Event]


@define(eq=False)
class Arity0Function:
    _body: Callable[[], Event]

    def __call__(self, arg: Call) -> Event:
        assert_arity(arg, arity=0)
        return self._body()

    @classmethod
    def const(cls, event: Event) -> Arity0Function:
        """Create a function which always returns the specified event."""
        return cls(lambda: event)


@define(eq=False)
class Arity1Function:
    _body: Callable[[Call], Event]

    def __call__(self, arg: Call) -> Event:
        assert_arity(arg, arity=1)
        return self._body(arg.args[0])


BUILT_IN_FUNCTIONS = {
    # /////
}
