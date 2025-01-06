
from __future__ import annotations

from wuas.floornumber import FloorNumber

from enum import Enum


class Direction(Enum):
    """Direction constants for the four cardinal directions."""

    UP = 'up'
    LEFT = 'left'
    RIGHT = 'right'
    DOWN = 'down'

    def as_tuple2(self) -> tuple[int, int]:
        if self == Direction.UP:
            return 0, -1
        elif self == Direction.LEFT:
            return -1, 0
        elif self == Direction.RIGHT:
            return 1, 0
        elif self == Direction.DOWN:
            return 0, 1

    def as_tuple3(self) -> tuple[int, int, FloorNumber]:
        return self.as_tuple2() + (FloorNumber(0),)

    def opposite(self) -> Direction:
        if self == Direction.UP:
            return Direction.DOWN
        elif self == Direction.LEFT:
            return Direction.RIGHT
        elif self == Direction.RIGHT:
            return Direction.LEFT
        elif self == Direction.DOWN:
            return Direction.UP
