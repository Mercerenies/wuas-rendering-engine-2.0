
"""Helper functions useful throughout the program."""

from __future__ import annotations

from typing import Iterator, Any
import math
from pathlib import Path
import importlib
import os
import os.path

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


def walk_files_relative(root_dir: Path | str) -> Iterator[Path]:
    """Returns paths relative to directory."""
    if isinstance(root_dir, str):
        root_dir = Path(root_dir)
    for dir, _, filenames in root_dir.walk():
        for filename in filenames:
            yield dir.relative_to(root_dir) / filename


def import_immediate_submodules(
    current_file: str,
    current_module_name: str,
    *,
    include_folders: bool = True,
) -> None:
    """Imports all immediate submodules of the module given by the
    argument file path and argument module name. The first two
    arguments should generally be __file__ and __name__.

    If include_folders is True (the default), then immediate
    subfolders which contain __init__.py will also be imported. If
    False, then only .py files in the current directory are imported.

    """
    current_module_name = current_module_name.removesuffix('__init__')
    for file in os.listdir(os.path.dirname(current_file)):
        if file.endswith('.py') and file != '__init__.py':
            module_name = f'{current_module_name}.{file[:-3]}'
            importlib.import_module(module_name)
        elif include_folders:
            full_path = os.path.join(os.path.dirname(current_file), file)
            init_py = os.path.join(full_path, '__init__.py')
            if os.path.isdir(full_path) and os.path.isfile(init_py):
                module_name = f'{current_module_name}.{file}'
                importlib.import_module(module_name)
