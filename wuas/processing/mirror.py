
"""Board processor which mirrors the board horizontally. Simplified
version of game2024_mirror, which also attempts to preserve player
locations."""

from __future__ import annotations

from wuas.processing.abc import BoardProcessor
from wuas.board import Board, Floor
from wuas.config import ConfigFile
from wuas.processing.registry import registered_processor


@registered_processor(aliases=["mirror"])
class MirrorProcessor(BoardProcessor):

    def run(self, config: ConfigFile, board: Board) -> None:
        for floor in board.floors.values():
            self._mirror_floor(floor)

    def _mirror_floor(self, floor: Floor) -> None:
        width = floor.width
        for x0, y in floor.indices:
            x1 = width - 1 - x0
            if x0 < x1:
                floor.tiles[x0, y], floor.tiles[x1, y] = floor.tiles[x1, y], floor.tiles[x0, y]
