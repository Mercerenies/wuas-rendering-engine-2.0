
"""The dirt/grass/tree/ash terrain spread mechanics from the 2023 game."""

from __future__ import annotations

from wuas.processing.abc import BoardProcessor
from wuas.board import Board, Floor
from wuas.config import ConfigFile
from wuas.processing.registry import registered_processor

from copy import deepcopy
import random

# I'm not going to pretend this fits into some .json configuration data. I'm
# special-casing the rules.


@registered_processor(aliases=["terrain2023"])
class TerrainProcessor(BoardProcessor):

    def run(self, config: ConfigFile, board: Board) -> None:
        original_board = deepcopy(board)
        for z, floor in board.floors.items():
            for x, y in floor.indices:
                space = floor.get_space(x, y)
                adjacent = _get_adjacent_spaces(original_board.floors[z], x, y)
                space.space_name = _evaluate_terrain(space.space_name, adjacent)


def _get_adjacent_spaces(floor: Floor, x: int, y: int) -> list[str]:
    result = []
    targets = [
        (x - 1, y - 1), (x    , y - 1), (x + 1, y - 1),  # noqa: E202, E203
        (x - 1, y    ),                 (x + 1, y    ),  # noqa: E202, E203
        (x - 1, y + 1), (x    , y + 1), (x + 1, y + 1),  # noqa: E202, E203
    ]
    for target in targets:
        tx, ty = target
        if floor.in_bounds(tx, ty):
            result.append(floor.get_space(tx, ty).space_name)
        else:
            result.append("gap")
    return result


def _evaluate_terrain(current_space: str, adjacent_spaces: list[str]) -> str:
    match current_space:
        case "ash":
            # Ash spaces will absorb nearby grass, tree, and water spaces.
            candidates = {"grass", "tree", "water"} & set(adjacent_spaces)
            if candidates:
                return random.choice(list(candidates))
            else:
                return "ash"
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
