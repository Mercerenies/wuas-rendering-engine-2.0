
from .turn import WuasTurn
from .singleplayer import SinglePlayerBoard
from .events import EventState
from .logs import MessageLogger
from .names import ObjectNamer, ConfigObjectNamer
from .parser import WuasTurnParser
from wuas.config import ConfigFile
from wuas.board import Board

from attrs import define


__all__ = (
    'WuasTurnEvaluator',
    'WuasTurn', 'WuasTurnParser',
    'SinglePlayerBoard', 'EventState',
)


@define(eq=False)
class WuasTurnEvaluator:
    _config: ConfigFile
    _board: Board

    def evaluate_turn(self, turn: WuasTurn, player_id: str) -> list[str]:
        local_board = SinglePlayerBoard(
            board=self._board,
            player_id=player_id,
        )
        logger = MessageLogger()
        state = EventState(
            logger=logger,
            board=local_board,
            namer=self.namer,
        )
        for event in turn.filtered_events(player_id=player_id):
            event.execute(state)
        return list(logger.messages())

    @property
    def namer(self) -> ObjectNamer:
        return ConfigObjectNamer(self._config)


class NoSuchPlayerError(Exception):
    pass
