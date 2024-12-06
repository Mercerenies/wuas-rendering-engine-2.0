
"""Board processor which mirrors the board horizontally but attempts
to leave players at the "original" position.

Specifically, the board is considered to have mirrored across the
column containing the Altar. Any player should attempt to stay at
their original position (relative to the Altar). If that position
turns out to be a gap in the new configuration, then (and only then)
should that player warp to the new mirrored position.

 It also assumes the board is a torus (therefore things wrap around).

"""

from __future__ import annotations

from wuas.board import Board, ConcreteToken, move_token
from wuas.config import ConfigFile, normalize_space_name
from wuas.processing.registry import registered_processor
from wuas.processing.mirror import MirrorProcessor

import sys
from typing import TypeVar, NamedTuple, Iterator


_T = TypeVar("_T")


@registered_processor(aliases=['mirror2024'])
class MirrorWithPlayersProcessor(MirrorProcessor):

    def run(self, config: ConfigFile, board: Board) -> None:
        super().run(config, board)
        altar_x, _, _ = _find_altar(board)
        tokens = list(_find_players(config, board))
        for player_token in tokens:
            _try_to_move_back(config, board, altar_x, player_token.pos, player_token.token_id)


class PlayerToken(NamedTuple):
    pos: tuple[int, int, int]
    token_id: str


def _find_players(config: ConfigFile, board: Board) -> Iterator[PlayerToken]:
    for x, y, z in board.indices:
        for token_id in board.get_space(x, y, z).token_ids:
            token = board.tokens[token_id]
            if isinstance(token, ConcreteToken) and config.definitions.get_token(token.token_name).is_player():
                yield PlayerToken((x, y, z), token_id=token.token_name)


def _find_altar(board: Board) -> tuple[int, int, int]:
    for x, y, z in board.indices:
        if board.get_space(x, y, z).space_name == ALTAR_NAME:
            return x, y, z
    raise ValueError('Could not find altar in board')


def _try_to_move_back(
        config: ConfigFile,
        board: Board,
        altar_x: int,
        pos: tuple[int, int, int],
        token_id: str,
) -> None:
    # We just mirrored everything, including player tokens. Try to
    # un-mirror this player token.
    x, y, z = pos
    dest_x = (2 * altar_x - x) % board.width
    dest_space = board.get_space(dest_x, y, z)
    space_name = normalize_space_name(dest_space.space_name)
    if space_name != GAP_NAME and space_name not in config.meta.get('mirrorsolids', []):
        # Move the player back to the destination.
        move_token(board, token_id, src=(x, y, z), dest=(dest_x, y, z))
        print(f"Mirror: Player {token_id} remained at the same X/Y coords", file=sys.stderr)
    else:
        print(f"Mirror: Player {token_id} moved with the board", file=sys.stderr)


ALTAR_NAME = 'altar'
GAP_NAME = 'gap'
