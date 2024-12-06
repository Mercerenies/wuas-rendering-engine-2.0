
"""Board processor which moves balloons."""

from __future__ import annotations

from wuas.config import ConfigFile
from wuas.processing.abc import BoardProcessor
from wuas.board import Board, Space, delete_token, move_token
from wuas.processing.registry import registered_processor

from typing import Callable, ClassVar, Optional
from dataclasses import dataclass
from collections import Counter
import random


@registered_processor(aliases=['balloons2024'])
class BalloonMoveProcessor(BoardProcessor):
    """Board processor which moves all tokens identifying as a balloon.

    The default processor identifies tokens with name "balloon" and
    moves them 1 to 3 spaces at random, though this behavior can be
    overridden with a specific constructor call.

    Assumes the direction of gravity is UP. This script will have to
    be updated if that changes.

    """
    config: BalloonMoveConfig

    def __init__(self, config: BalloonMoveConfig | None = None) -> None:
        if config is None:
            config = BalloonMoveConfig()
        self.config = config

    def run(self, config: ConfigFile, board: Board) -> None:
        _already_moved_balloons: Counter[tuple[int, int, int]] = Counter()
        for x, y, z in board.indices:
            tile = board.get_space(x, y, z)
            balloon_count = self._count_balloons(tile) - _already_moved_balloons[(x, y, z)]
            for _ in range(balloon_count):
                dest = self._move_balloon(board, src=(x, y, z))
                if dest:
                    _already_moved_balloons[dest] += 1

    def _count_balloons(self, tile: Space) -> int:
        count = 0
        for token in tile.get_tokens():
            if token.name == self.config.token_id:
                count += 1
        return count

    def _move_balloon(self, board: Board, src: tuple[int, int, int]) -> Optional[tuple[int, int, int]]:
        x, y, z = src
        dest_y = y - self.config.move_speed()
        if dest_y < 0:
            # If we're above the board AND the board wraps, then wrap.
            # Otherwise, delete but don't move.
            if self.config.board_wraps:
                dest_y += board.height
            else:
                delete_token(board, token_id=self.config.token_id, src=(x, y, z))
                return None
        move_token(board, token_id=self.config.token_id, src=(x, y, z), dest=(x, dest_y, z))
        return (x, dest_y, z)


@dataclass
class BalloonMoveConfig:
    token_id: str = "balloon"
    move_speed: Callable[[], int] = lambda: random.randint(1, 3)
    board_wraps: bool = True

    DEFAULT: ClassVar[BalloonMoveConfig]


BalloonMoveConfig.DEFAULT = BalloonMoveConfig()
