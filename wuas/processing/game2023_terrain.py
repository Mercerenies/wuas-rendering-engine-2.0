
"""The dirt/grass/tree terrain spread mechanics from the 2023 game."""

from __future__ import annotations

from wuas.processing.abc import BoardProcessor
from wuas.board import Board
from wuas.config import ConfigFile
from wuas.processing.registry import registered_processor

from copy import deepcopy

# I'm not going to pretend this fits into some .json configuration data. I'm
# special-casing the rules.


@registered_processor
class TerrainProcessor(BoardProcessor):

    def run(self, config: ConfigFile, board: Board) -> None:
        original_board = deepcopy(board)
        for x, y in board.indices:
            space = board.get_space(x, y)
            adjacent = _get_adjacent_spaces(original_board, x, y)
            space.space_name = _evaluate_terrain(space.space_name, adjacent)

def _get_adjacent_spaces(board: Board, x: int, y: int) -> list[str]:
    result = []
    targets = [
        (x - 1, y - 1), (x    , y - 1), (x + 1, y - 1),
        (x - 1, y    ),                 (x + 1, y    ),
        (x - 1, y + 1), (x    , y + 1), (x + 1, y + 1),
    ]
    for target in targets:
        tx, ty = target
        if board.in_bounds(tx, ty):
            result.append(board.get_space(tx, ty).space_name)
        else:
            result.append("gap")
    return result


def _evaluate_terrain(current_space: str, adjacent_spaces: list[str]) -> str:
    match current_space:
        case "dirt":
            if 'water' in adjacent_spaces or adjacent_spaces.count('grass') in [2, 3]:
                return 'grass'
            else:
                return 'dirt'
        case "grass":
            grass_tiles = adjacent_spaces.count('grass')
            if grass_tiles < 2:
                return 'dirt'
            elif grass_tiles > 3:
                return 'tree'
            else:
                return 'grass'
        case "tree":
            if adjacent_spaces.count('grass') <= 1:
                return 'grass'
            else:
                return 'tree'
        case _:
            # No expansion
            return current_space
