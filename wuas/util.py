
"""Helper functions useful throughout the program."""

from __future__ import annotations

from typing import Iterator


def lerp(a: float, b: float, amount: float) -> float:
    """Linear interpolation between a and b, using amount as the
    interpolation factor. If amount is not between 0 and 1, then this
    function extrapolateslinearly."""
    return a * (1 - amount) + b * amount


def manhattan_circle(origin: tuple[int, int, int], distance: int) -> Iterator[tuple[int, int, int]]:
    xorigin, yorigin, zorigin = origin
    for dx in range(- distance, distance + 1):
        yrange = distance - abs(dx)
        for dy in range(- yrange, yrange + 1):
            zrange = distance - abs(dx) - abs(dy)
            for dz in range(- zrange, zrange + 1):
                yield (xorigin + dx, yorigin + dy, zorigin + dz)
