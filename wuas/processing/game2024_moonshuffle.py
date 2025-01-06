
"""Board processor which shuffles non-player tokens for the Majora
Moon effect."""

from __future__ import annotations

from wuas.config import ConfigFile
from wuas.processing.abc import BoardProcessor
from wuas.board import Board, Token, HiddenToken, move_token
from wuas.processing.registry import registered_processor

from dataclasses import dataclass
import random


@registered_processor(aliases=['shuffle2024'])
class MoonShuffleProcessor(BoardProcessor):
    """Board processor which moves all non-player tokens to random
    positions on the board.

    Every token EXCEPT player tokens and gold coins will be moved to a
    random position on the board. Any position on the board is a valid
    target, except for Start and the Altar.

    """

    def run(self, config: ConfigFile, board: Board) -> None:
        tokens_to_move = _find_all_targets(config, board)
        valid_destinations = _get_valid_destinations(board)
        for token in tokens_to_move:
            new_position = random.choice(valid_destinations)
            move_token(
                board=board,
                token_id=token.token_id,
                src=token.source_pos,
                dest=new_position,
            )


@dataclass(frozen=True)
class TargetToken:
    source_pos: tuple[int, int, int]
    token_id: str


def _find_all_targets(config: ConfigFile, board: Board) -> list[TargetToken]:
    valid_targets = []
    for pos in board.indices:
        tile = board.get_space(pos)
        for token in tile.get_tokens():
            if _is_valid_target(config=config, token=token):
                valid_targets.append(TargetToken(source_pos=pos, token_id=token.name))
    return valid_targets


def _is_valid_target(config: ConfigFile, token: Token) -> bool:
    if isinstance(token, HiddenToken):
        return True
    if token.token_name == 'goldcoin':
        return False
    token_definition = config.definitions.get_token(token.token_name)
    return not token_definition.is_player()


def _get_valid_destinations(board: Board) -> list[tuple[int, int, int]]:
    positions = []
    for pos in board.indices:
        tile = board.get_space(pos)
        if tile.space_name not in ('start', 'altar'):
            positions.append(pos)
    return positions
