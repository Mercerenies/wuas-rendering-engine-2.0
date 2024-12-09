
from __future__ import annotations

from typing import ClassVar, Sequence, NamedTuple, Iterator
from dataclasses import dataclass
from itertools import chain

from attrs import define, field

from .events import Event


type TurnKey = PlayerTurnKey | Global


@define(frozen=True)
class WuasTurn:
    _segments: Sequence[TurnSegment] = field(converter=lambda xs: tuple(xs))

    def __iter__(self) -> Iterator[TurnSegment]:
        return iter(self._segments)

    def filtered(self, player_id: str) -> Iterator[TurnSegment]:
        """Returns an iterable of all segments of a turn that apply to
        the given player."""
        return filter(lambda segment: segment.key.applies_to(player_id), self)

    def filtered_events(self, player_id: str) -> Iterator[Event]:
        """Returns an iterable of events of a turn that apply to the
        given player."""
        return chain.from_iterable(map(lambda segment: segment.events, self.filtered(player_id)))


class TurnSegment(NamedTuple):
    """A segment of a turn consists of a key indicating to whom it
    belongs, as well as a sequence of zero or more events.

    """
    key: TurnKey
    events: Sequence[Event]


@dataclass(frozen=True)
class PlayerTurnKey:
    """Object acting as a key representing events local to a single
    player."""
    player_id: str

    def applies_to(self, target_id: str) -> bool:
        """A player's turn only applies to that player, not to any
        other players."""
        return self.player_id == target_id


class Global:
    """Sentinel object which acts as a key for events global to all
    players. This is a singleton object."""
    _INSTANCE: ClassVar[Global]

    KEY_NAME = "global"

    def __new__(cls) -> Global:
        return cls._INSTANCE

    def __repr__(self) -> str:
        return "Global()"

    def __str__(self) -> str:
        return "Global"

    def applies_to(self, target_id: str) -> bool:
        """A global turn segment applies to all players, regardless of
        their ID.

        """
        return True


Global._INSTANCE = object.__new__(Global)
