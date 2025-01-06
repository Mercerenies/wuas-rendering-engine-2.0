
"""Banish the outer ring of fire spaces to the MCotW."""

from __future__ import annotations

from wuas.processing.abc import BoardProcessor
from wuas.board import Board
from wuas.floornumber import FloorNumber
from wuas.config import ConfigFile
from wuas.processing.registry import registered_processor

import random

MCOTW = (
    FloorNumber(-100),
    FloorNumber(-101),
    FloorNumber(-102),
)


@registered_processor
class BanishOuterRingProcessor(BoardProcessor):

    def run(self, config: ConfigFile, board: Board) -> None:
        for i in range(board.width):
            # Top and bottom
            self._migrate(board, i, 0)
            self._migrate(board, i, board.height - 1)
        for j in range(board.height):
            # Left and right
            self._migrate(board, 0, j)
            self._migrate(board, board.width - 1, j)

    def _migrate(self, board: Board, x: int, y: int) -> None:
        new_z = random.choice(MCOTW)
        board.get_space(x, y, FloorNumber(0)).space_name = "ash"
        board.get_space(x, y, new_z).space_name = "fire"
