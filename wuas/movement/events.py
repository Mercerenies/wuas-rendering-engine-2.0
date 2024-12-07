
from __future__ import annotations

# from .prolog import HornClause, Call
from .logs import MessageLogger
from .singleplayer import SinglePlayerBoard
from .names import PlayerNamer

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable


class Event(ABC):
    """An event mutates the board and potentially logs one or more
    messages to a message logger.

    """

    @abstractmethod
    def execute(self, state: EventState) -> None:
        """Runs the event, mutating the board in the process. Any
        significant actions that occur shall be logged to the message
        logger.

        """
        ...


@dataclass(frozen=True, kw_only=True)
class EventState:
    logger: MessageLogger
    board: SinglePlayerBoard
    namer: PlayerNamer


class SimpleMessage(Event):
    """An event which does not mutate the board and merely logs a
    message."""
    _message: Callable[[str], str]

    def __init__(self, message_or_template: str | Callable[[str], str], /) -> None:
        if callable(message_or_template):
            self._message = message_or_template
        else:
            self._message = lambda message: message_or_template

    def execute(self, state: EventState) -> None:
        player_name = state.namer.get_name(state.board.player_id)
        state.logger.log(self._message(player_name))
