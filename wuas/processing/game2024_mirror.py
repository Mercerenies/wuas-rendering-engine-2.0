
"""Board processor which mirrors the board horizontally but attempts
to leave players at the "original" position.

Specifically, the board is considered to have mirrored across the
column containing the Altar. Any player should attempt to stay at
their original position (relative to the Altar). If that position
turns out to be a gap in the new configuration, then (and only then)
should that player warp to the new mirrored position.

"""

from __future__ import annotations

from wuas.processing.abc import BoardProcessor
from wuas.board import Board
from wuas.config import ConfigFile, normalize_space_name
from wuas.processing.registry import registered_processor
from wuas.processing.mirror import MirrorProcessor

from typing import Sequence, TypeVar, NamedTuple, Iterator


_T = TypeVar("_T")


@registered_processor(aliases=['mirror2024'])
class MirrorWithPlayersProcessor(BoardProcessor):

    def run(self, config: ConfigFile, board: Board) -> None:
        MirrorProcessor().run(config, board)
        altar_x, _, _ = _find_altar(board)
        tokens = list(_find_players(config, board))
        for player_token in tokens:
            _try_to_move_back(board, altar_x, player_token.pos, player_token.token_id)


class PlayerToken(NamedTuple):
    pos: tuple[int, int, int]
    token_id: str


def _find_players(config: ConfigFile, board: Board) -> Iterator[PlayerToken]:
    for x, y, z in board.indices:
        for token_id in board.get_space(x, y, z).token_ids:
            token = board.tokens[token_id]
            if config.definitions.get_token(token.token_name).is_player():
                yield PlayerToken((x, y, z), token_id)


def _find_altar(board: Board) -> tuple[int, int, int]:
    for x, y, z in board.indices:
        if board.get_space(x, y, z).space_name == ALTAR_NAME:
            return x, y, z
    raise ValueError('Could not find altar in board')


def _try_to_move_back(board: Board, altar_x: int, pos: tuple[int, int, int], token_id: str) -> None:
    # We just mirrored everything, including player tokens. Try to
    # un-mirror this player token."""
    x, y, z = pos
    src_space = board.get_space(x, y, z)
    dest_x = 2 * altar_x - x
    try:
        dest_space = board.get_space(dest_x, y, z)
    except IndexError:
        # Un-mirrored position is out of bounds; assume it's a gap.
        return
    if normalize_space_name(dest_space.space_name) != GAP_NAME:
        # Move the player back to the destination.
        src_space.token_ids = _without(src_space.token_ids, token_id)
        dest_space.token_ids = tuple(dest_space.token_ids) + (token_id,)


def _without(seq: Sequence[_T], value: _T) -> Sequence[_T]:
    """Remove first instance of value in seq, without modifying the
    original sequence. If value is not in seq, does nothing."""
    seq = list(seq)
    try:
        seq.remove(value)
    except ValueError:
        pass
    return seq


ALTAR_NAME = 'altar'
GAP_NAME = 'gap'
