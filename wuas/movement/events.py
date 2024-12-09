
from __future__ import annotations

from .logs import MessageLogger
from .singleplayer import SinglePlayerBoard
from .names import ObjectNamer
from .direction import Direction
from wuas.processing.game2024_mirror import MirrorWithPlayersProcessor, MovementExplanation
from wuas.config import ConfigFile

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, NewType, Protocol, Sequence, Iterable
from collections import defaultdict

from attrs import define


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


@dataclass(kw_only=True)
class EventState:
    logger: MessageLogger
    board: SinglePlayerBoard
    namer: ObjectNamer
    config: ConfigFile
    meta: dict[EventMetaKey, object] = field(init=False, default_factory=lambda: defaultdict(lambda: None))


# An EventMetaKey shall be qualified by the defining module. So a key
# in, for example, wuas.movement.parser.functions shall be prefixed
# with "wuas.movement.parser.functions.*"
EventMetaKey = NewType("EventMetaKey", str)


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
        player_name = state.namer.get_player_name(state.board.player_id)
        state.logger.log(self._message(player_name))


CONTROLS_REVERSED_KEY = EventMetaKey("wuas.movement.events.CONTROLS_REVERSED_KEY")


class ReverseControlsEvent(Event):
    def execute(self, state: EventState) -> None:
        state.meta[CONTROLS_REVERSED_KEY] = True
        state.logger.log("Controls are reversed.")


class ShotWithSabotageGunEvent(Event):
    def execute(self, state: EventState) -> None:
        state.meta[CONTROLS_REVERSED_KEY] = not state.meta[CONTROLS_REVERSED_KEY]
        player_name = state.namer.get_player_name(state.board.player_id)
        verb = "reversed" if state.meta[CONTROLS_REVERSED_KEY] else "un-reversed"
        state.logger.log(f"{player_name} has been shot with the **Sabotage Gun**. Controls are now {verb}.")


@define(eq=False)
class UserInputEvent(Event):
    _inputs: Sequence[Direction]

    def execute(self, state: EventState) -> None:
        player_name = state.namer.get_player_name(state.board.player_id)
        original_inputs = ', '.join([d.name for d in self._inputs])
        message = f"{player_name} attempts to move: {original_inputs}."
        if state.meta[CONTROLS_REVERSED_KEY]:
            reversed_inputs = ', '.join([d.opposite().name for d in self._inputs])
            message += f" Because controls are reversed, this is interpreted as: {reversed_inputs}."
        state.logger.log(message)


@define(eq=False)
class TurnStartEvent(Event):

    def message(self, player_name: str, space_name: str) -> str:
        return f"{player_name} begins their turn on **{space_name}**."

    def execute(self, state: EventState) -> None:
        player_name = state.namer.get_player_name(state.board.player_id)
        player_pos = state.board.player_pos
        space_name = state.namer.get_space_name(state.board.board.get_space(player_pos).space_name)
        state.logger.log(self.message(player_name=player_name, space_name=space_name))


@define(eq=False)
class MovementEvent(Event):
    direction: Direction
    _custom_message: MovementEventCustomMessage | None = None

    def message(self, player_name: str, space_name: str) -> str:
        if self._custom_message is None:
            return f"{player_name} moves **{self.direction.name}**, onto **{space_name}**."
        else:
            return self._custom_message(player_name=player_name, space_name=space_name)

    def execute(self, state: EventState) -> None:
        dest = state.board.move_player(delta=self.direction.as_tuple3())
        player_name = state.namer.get_player_name(state.board.player_id)
        dest_space_id = state.board.board.get_space(dest).space_name
        dest_space_name = state.namer.get_space_name(dest_space_id)
        state.logger.log(self.message(player_name=player_name, space_name=dest_space_name))

    @classmethod
    def by_gravity(cls, direction: Direction = Direction.DOWN):
        def _message(*, player_name: str, space_name: str) -> str:
            return f"{player_name} falls **{direction.name}** due to gravity, onto **{space_name}**."
        return cls(direction=direction, custom_message=_message)


class MovementEventCustomMessage(Protocol):
    def __call__(self, *, player_name: str, space_name: str) -> str:
        ...


class MirrorBoardEvent(Event):
    _processor: MirrorWithPlayersProcessor

    def __init__(self) -> None:
        self._processor = MirrorWithPlayersProcessor()

    def execute(self, state: EventState) -> None:
        msg = "The board has been mirrored."
        with state.board.moving_player() as board:
            summary = self._processor.run_with_summary(config=state.config, board=board)
        explanation = MirrorBoardEvent._find_matching_player(
            player_id=state.board.player_id,
            summary=summary,
        )
        player_name = state.namer.get_player_name(state.board.player_id)
        space_name = state.namer.get_space_name(state.board.player_space.space_name)
        if explanation.moved_with_board:
            target_space_name = state.namer.get_space_name(explanation.space_at_original_coords)
            msg += f" {player_name} could not remain at the same X/Y position due to **{target_space_name}** in the way, so they remain on **{space_name}**."
        else:
            msg += f" {player_name} was able to remain at the same X/Y position and is now on **{space_name}**."
        state.logger.log(msg)

    @staticmethod
    def _find_matching_player(player_id: str, summary: Iterable[MovementExplanation]) -> MovementExplanation:
        for explanation in summary:
            if explanation.player_id == player_id:
                return explanation
        raise ValueError(f"Could not find player with id {player_id!r} in summary {summary!r}")
