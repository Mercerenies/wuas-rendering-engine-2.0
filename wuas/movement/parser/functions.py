
"""Built-in functions available in the movement language API.

For the purposes of this module, a WUAS movement Function is a
callable object which takes a Prolog Call and produces an Event,
raising a ParseError on failure.

"""

from __future__ import annotations

from typing import Callable, Mapping
from attrs import define
from enum import Enum

from wuas.movement.prolog import Call
from wuas.movement.direction import Direction
from wuas.movement.events import Event
from wuas.movement import events
from .assertions import assert_arity, assert_atom, assert_list
from .error import ParseError


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

    @classmethod
    def directional(cls, body: Callable[[Direction], Event]) -> Arity1Function:
        def _compile(arg: Call) -> Event:
            direction = Direction(assert_atom(arg))
            return body(direction)
        return cls(body=_compile)


def input_function() -> Function:
    def _compile(call: Call) -> Event:
        directions = [Direction(assert_atom(term)) for term in assert_list(call)]
        return events.UserInputEvent(inputs=directions)
    return Arity1Function(_compile)


def _lakitu_cloud_message(player_name: str) -> str:
    return f"{player_name} takes a **Lakitu Cloud**."


class CannotMoveReason(Enum):
    WATER = 'water'
    GAP = 'gap'

    def message(self, player_name: str) -> str:
        if self == CannotMoveReason.WATER:
            return f"{player_name} cannot proceed because they are in water."
        elif self == CannotMoveReason.GAP:
            return f"{player_name} cannot proceed because there is an empty gap in the way."


def cannot_move_function() -> Function:
    def _compile(arg: Call) -> Event:
        try:
            reason = CannotMoveReason(assert_atom(arg))
        except ValueError:
            raise ParseError(f"invalid cannot_move reason: {arg}")
        return events.SimpleMessage(reason.message)
    return Arity1Function(_compile)


BUILT_IN_FUNCTIONS: Mapping[str, Function]
BUILT_IN_FUNCTIONS = {
    "controls_reversed": Arity0Function.const(events.ReverseControlsEvent()),
    "input": input_function(),
    "shot_with_gun": Arity0Function.const(events.ShotWithSabotageGunEvent()),
    "go": Arity1Function.directional(events.MovementEvent),
    "gravity": Arity1Function.directional(events.MovementEvent.by_gravity),
    "take_lakitu_cloud": Arity0Function.const(events.SimpleMessage(_lakitu_cloud_message)),
    "mirror_board": Arity0Function.const(events.MirrorBoardEvent()),
    "cannot_move": cannot_move_function(),
    "start_turn": Arity0Function.const(events.TurnStartEvent()),
}
