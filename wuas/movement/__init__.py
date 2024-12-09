
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
        player_pos = _find_player(self._board, player_id)
        if not player_pos:
            raise NoSuchPlayerError(f"No such player {player_id}")
        local_board = SinglePlayerBoard(
            board=self._board,
            player_pos=player_pos,
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


def _find_player(board: Board, player_id: str) -> tuple[int, int, int] | None:
    for pos in board.indices:
        space = board.get_space(pos)
        if any(tok.name == player_id for tok in space.get_tokens()):
            return pos
    return None
