
"""The dirt/grass/tree/ash terrain spread mechanics from the 2023 game."""

from __future__ import annotations

from wuas.processing.abc import BoardProcessor
from wuas.board import Board, Floor, Space
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
                space.space_name = _evaluate_terrain(space, adjacent)


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


def _evaluate_terrain(current_space: Space, adjacent_spaces: list[str]) -> str:
    space_name = current_space.space_name
    match space_name:
        case "ash":
            # Ash spaces will absorb nearby grass, tree, and water spaces.
            candidates = {"grass", "tree", "water", "tgrass", "ttree", "twater"} & set(adjacent_spaces)
            if candidates:
                return random.choice(list(candidates))
            elif random.random() < 0.33 and 'smolderingimmunity' not in current_space.attribute_ids:
                return "dirt"
            else:
                return "ash"
        case "dirt":
            grass_tiles = adjacent_spaces.count('grass') + adjacent_spaces.count('tgrass')
            if 'water' in adjacent_spaces or grass_tiles in [2, 3]:
                return 'grass'
            else:
                return 'dirt'
        case "grass":
            grass_tiles = adjacent_spaces.count('grass') + adjacent_spaces.count('tgrass')
            if grass_tiles < 2:
                return 'dirt'
            elif grass_tiles > 3:
                return 'tree'
            else:
                return 'grass'
        case "tree":
            grass_tiles = adjacent_spaces.count('grass') + adjacent_spaces.count('tgrass')
            if 'ttree' in adjacent_spaces:
                return 'ttree'
            elif grass_tiles <= 1:
                return 'grass'
            else:
                return 'tree'
        case "tdirt":
            grass_tiles = adjacent_spaces.count('grass') + adjacent_spaces.count('tgrass')
            if 'water' in adjacent_spaces or grass_tiles in [2, 3]:
                return 'tgrass'
            else:
                return 'tdirt'
        case "tgrass":
            grass_tiles = adjacent_spaces.count('grass') + adjacent_spaces.count('tgrass')
            if grass_tiles < 2:
                return 'tdirt'
            elif grass_tiles > 3:
                return 'ttree'
            else:
                return 'tgrass'
        case _:
            # No expansion
            return space_name
