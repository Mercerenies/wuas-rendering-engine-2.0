
"""The lighting engine, originally designed for Turn 2 of the 2023
game.

"""

from __future__ import annotations

from wuas.processing.lighting.config import LightingConfig, ConfigLightSourceSupplier
from wuas.processing.lighting.source import LightSourceSupplier
from wuas.processing.abc import BoardProcessor
from wuas.processing.registry import registered_processor
from wuas.board import Board
from wuas.config import ConfigFile
from wuas.util import lerp

from typing import Iterable, Iterator


@registered_processor(aliases=["lighting"])
class LightingProcessor(BoardProcessor):

    def run(self, config: ConfigFile, board: Board) -> None:
        lighting_engine = LightingEngine(
            config=config,
            board=board,
        )
        lighting_engine.compute_all_lights()
        lighting_engine.darken_board()


class LightingEngine:
    _config: ConfigFile
    _board: Board
    _lighting_grid: LightingGrid
    _lighting_config: LightingConfig
    _light_sources: LightSourceSupplier

    def __init__(self, config: ConfigFile, board: Board) -> None:
        self._config = config
        self._board = board
        self._lighting_grid = LightingGrid(board.width, board.height)
        self._lighting_config = LightingConfig.from_json(config.meta['lighting'])
        # TODO Allow this to be constructed abstractly (as a ctor arg)
        self._light_sources = ConfigLightSourceSupplier(self._lighting_config, board)

    def compute_all_lights(self) -> None:
        self._lighting_grid.is_dirty = True
        while self._lighting_grid.is_dirty:
            self._lighting_grid.reset_dirty_bit()
            # Standard light sources
            for x, y in self._board.indices:
                light_level = self._light_sources.get_light_source((x, y))
                if light_level > 0:
                    self._do_light_emission((x, y), light_level)
            # Custom adjacency rules
            for x0, y0 in self._board.indices:
                space = self._board.get_space(x0, y0)
                adjacency_rule = self._lighting_config.adjacency.get(space.space_name, None)
                if self._lighting_grid[x0, y0] > 0 and adjacency_rule is not None:
                    for x1, y1 in self._board.indices:
                        target_space = self._board.get_space(x1, y1)
                        if target_space.space_name == adjacency_rule:
                            self._do_light_emission((x1, y1), self._lighting_grid[x0, y0] - 1)

    def _do_light_emission(self, position: tuple[int, int], power: int) -> None:
        for distance in range(power):
            for x, y in _manhattan_circle(position, distance):
                if self._board.in_bounds(x, y):
                    # Check if anything diminishes the light
                    dampened_light_level = power - distance
                    for x1, y1 in _get_intersected_spaces(position, (x, y)):
                        if (x1, y1) == (x, y):
                            # A dampening object will never dampen its own space.
                            continue
                        space_name = self._board.get_space(x1, y1).space_name
                        dampen_factor = self._lighting_config.diminishing.get(space_name, 0)
                        dampened_light_level -= dampen_factor
                    self._lighting_grid.update((x, y), dampened_light_level)

    def darken_board(self) -> None:
        for x, y in self._board.indices:
            space = self._board.get_space(x, y)
            if self._lighting_grid[x, y] <= 0:
                space.space_name = self._lighting_config.darkness
                space.token_ids = []


class LightingGrid:
    is_dirty: bool
    _grid: list[list[int]]

    def __init__(self, width: int, height: int) -> None:
        self.is_dirty = False
        self._grid = [[0] * width for _ in range(height)]

    def __getitem__(self, index: tuple[int, int]) -> int:
        x, y = index
        return self._grid[y][x]

    def update(self, index: tuple[int, int], new_light: int) -> None:
        x, y = index
        old_light = self._grid[y][x]
        new_light = max(self._grid[y][x], new_light)
        self._grid[y][x] = new_light
        if old_light != new_light:
            self.is_dirty = True

    def reset_dirty_bit(self) -> None:
        self.is_dirty = False


def _manhattan_circle(origin: tuple[int, int], distance: int) -> Iterator[tuple[int, int]]:
    xorigin, yorigin = origin
    for dx in range(- distance, distance + 1):
        yrange = distance - abs(dx)
        for dy in range(- yrange, yrange + 1):
            yield (xorigin + dx, yorigin + dy)


def _get_intersected_spaces(origin: tuple[int, int], destination: tuple[int, int]) -> Iterable[tuple[int, int]]:
    xorigin, yorigin = (origin[0] + 0.5, origin[1] + 0.5)
    xdest, ydest = (destination[0] + 0.5, destination[1] + 0.5)
    result = set()
    for i in range(50):
        x = lerp(xorigin, xdest, i / 50)
        y = lerp(yorigin, ydest, i / 50)
        result.add((int(x), int(y)))
    return result
