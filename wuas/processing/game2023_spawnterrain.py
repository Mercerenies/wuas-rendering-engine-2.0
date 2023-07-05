
"""Southbridge's wish on turn 3, filling in on blank spaces and expanding the board."""

from __future__ import annotations

from wuas.processing.abc import BoardProcessor
from wuas.board import Board
from wuas.config import ConfigFile
from wuas.processing.registry import registered_processor

import random


@registered_processor
class SpawnTerrainProcessor(BoardProcessor):

    def run(self, config: ConfigFile, board: Board) -> None:
        board.resize(3, 3, 3, 3, "")
        for floor in board.floors.values():
            for x, y in floor.indices:
                space = floor.get_space(x, y)
                if space.space_name == '':
                    space.space_name = random.choice(['tree', 'dirt', 'grass'])
