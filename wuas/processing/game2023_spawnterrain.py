
"""Southbridge's wish on turn 3, filling in on blank spaces and expanding the board."""

from __future__ import annotations

from wuas.processing.abc import BoardProcessor
from wuas.board import Board
from wuas.config import ConfigFile

from copy import deepcopy
import random


class SpawnTerrainProcessor(BoardProcessor):

    def run(self, config: ConfigFile, board: Board) -> None:
        board.resize(3, 3, 3, 3, "")
        for x, y in board.indices:
            space = board.get_space(x, y)
            if space.space_name == '':
                space.space_name = random.choice(['tree', 'dirt', 'grass'])
