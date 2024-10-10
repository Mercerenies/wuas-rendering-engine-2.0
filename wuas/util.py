
"""Helper functions useful throughout the program."""

from __future__ import annotations

from typing import Iterator, Any
import math

from PIL import ImageDraw


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


def draw_dotted_line(draw: ImageDraw.ImageDraw,
                     pos0: tuple[float, float],
                     pos1: tuple[float, float],
                     fill: Any = None,
                     width: int = 0,
                     joint: Any = None,
                     dash_width: int = 4,
                     gap_width: int = 2) -> None:
    x0, y0 = pos0
    x1, y1 = pos1
    angle = math.atan2(y1 - y0, x1 - x0)
    distance = math.hypot(x0 - x1, y0 - y1)
    t = 0
    while t < distance:
        t1 = min(t + dash_width, distance)
        xx0 = x0 + t * math.cos(angle)
        xx1 = x0 + t1 * math.cos(angle)
        yy0 = y0 + t * math.sin(angle)
        yy1 = y0 + t1 * math.sin(angle)
        draw.line(((xx0, yy0), (xx1, yy1)), fill=fill, width=width, joint=joint)
        t += dash_width + gap_width
