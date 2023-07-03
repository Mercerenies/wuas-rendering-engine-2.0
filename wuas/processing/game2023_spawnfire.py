
"""Evan's wish on turn 3, filling in on blank spaces and expanding the board."""

from __future__ import annotations

from wuas.processing.abc import BoardProcessor
from wuas.board import Board
from wuas.config import ConfigFile

from copy import deepcopy
import random


class SpawnFireProcessor(BoardProcessor):

    def run(self, config: ConfigFile, board: Board) -> None:
        board.resize(1, 1, 1, 1, "fire")
