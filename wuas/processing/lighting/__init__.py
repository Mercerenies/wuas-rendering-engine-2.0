
"""The lighting engine, originally designed for Turn 2 of the 2023
game.

"""

from __future__ import annotations

from wuas.processing.lighting.config import LightingConfig, Game2023LightSourceSupplier
from wuas.processing.lighting.source import LightSourceSupplier
from wuas.processing.abc import BoardProcessor
from wuas.processing.registry import registered_processor
from wuas.board import Board
from wuas.floornumber import FloorNumber
from wuas.config import ConfigFile
from wuas.util import lerp, manhattan_circle

from typing import Iterable
import math


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
        self._lighting_grid = LightingGrid(board.width, board.height, board.floors)
        self._lighting_config = LightingConfig.from_json(config.meta['lighting'])
        # TODO Allow this to be constructed abstractly (as a ctor arg)
        self._light_sources = Game2023LightSourceSupplier(self._lighting_config, board)

    def compute_all_lights(self) -> None:
        self._lighting_grid.is_dirty = True
        while self._lighting_grid.is_dirty:
            self._lighting_grid.reset_dirty_bit()
            # Standard light sources
            for x, y, z in self._board.indices:
                light_level = self._light_sources.get_light_source((x, y, z))
                if light_level > 0:
                    self._do_light_emission((x, y, z), light_level)
            # Custom adjacency rules
            for x0, y0, z0 in self._board.indices:
                space = self._board.get_space(x0, y0, z0)
                adjacency_rule = self._lighting_config.adjacency.get(space.space_name, None)
                if self._lighting_grid[x0, y0, z0] > 0 and adjacency_rule is not None:
                    for x1, y1, z1 in self._board.indices:
                        target_space = self._board.get_space(x1, y1, z1)
                        if target_space.space_name == adjacency_rule:
                            self._do_light_emission((x1, y1, z1), self._lighting_grid[x0, y0, z0] - 1)

    def _do_light_emission(self, position: tuple[int, int, FloorNumber], power: int) -> None:
        for distance in range(power):
            for x, y, z in manhattan_circle(position, distance):
                if self._board.in_bounds(x, y, z):
                    # Check if anything diminishes the light
                    dampened_light_level = power - distance
                    if not z.is_infinite() and not position[2].is_infinite():
                        x0, y0, z0 = position
                        # At infinity, the concept of distance is
                        # meaningless, so don't try to compute it.
                        for x1, y1, z1 in _get_intersected_spaces((x0, y0, z0.as_integer()), (x, y, z.as_integer())):
                            if (x1, y1, z1) == (x, y, z):
                                # A dampening object will never dampen its own space.
                                continue
                            if not self._board.in_bounds(x, y, z):
                                # The board isn't convex anymore, since
                                # floors is a sparse array.
                                continue
                            space_name = self._board.get_space(x1, y1, FloorNumber(z1)).space_name
                            dampen_factor = self._lighting_config.diminishing.get(space_name, 0)
                            dampened_light_level -= dampen_factor
                    self._lighting_grid.update((x, y, z), dampened_light_level)

    def darken_board(self) -> None:
        for x, y, z in self._board.indices:
            space = self._board.get_space(x, y, z)
            if self._lighting_grid[x, y, z] <= 0:
                space.space_name = self._lighting_config.darkness
                space.token_ids = []
                space.attribute_ids = []


class LightingGrid:
    """The lighting grid consists of a two-dimensional grid of integers
    and a dirty bit. The dirty bit is publicly read-write and can be
    used to run a lighting loop until a steady state is reached."""

    is_dirty: bool
    _grid: dict[FloorNumber, list[list[int]]]
    _width: int
    _height: int

    def __init__(self, width: int, height: int, floors: Iterable[FloorNumber]) -> None:
        """Constructs a lighting grid of the given width and height
        where all values are initially zero."""
        self.is_dirty = False
        self._grid = {}
        for floor in floors:
            self._grid[floor] = [[0] * width for _ in range(height)]

    def __getitem__(self, index: tuple[int, int, FloorNumber]) -> int:
        """Get the light at the given position. Raises KeyError if out
        of bounds."""
        x, y, z = index
        return self._grid[z][y][x]

    def update(self, index: tuple[int, int, FloorNumber], new_light: int) -> None:
        """Set the light level at the given position to the maximum of
        its current value and the proposed new value. If this actually
        ends up changing the value, then this method sets is_dirty to
        true."""
        x, y, z = index
        old_light = self._grid[z][y][x]
        new_light = max(self._grid[z][y][x], new_light)
        self._grid[z][y][x] = new_light
        if old_light != new_light:
            self.is_dirty = True

    def reset_dirty_bit(self) -> None:
        """Set is_dirty to false."""
        self.is_dirty = False


def _get_intersected_spaces(origin: tuple[int, int, int],
                            destination: tuple[int, int, int]) -> Iterable[tuple[int, int, int]]:
    xorigin, yorigin, zorigin = (origin[0] + 0.5, origin[1] + 0.5, origin[2] + 0.5)
    xdest, ydest, zdest = (destination[0] + 0.5, destination[1] + 0.5, destination[2] + 0.5)
    result = set()
    for i in range(50):
        x = lerp(xorigin, xdest, i / 50)
        y = lerp(yorigin, ydest, i / 50)
        z = lerp(zorigin, zdest, i / 50)
        result.add((int(math.floor(x)), int(math.floor(y)), int(math.floor(z))))
    return result
