
"""Helper functions useful throughout the program."""

from __future__ import annotations

from typing import Iterator, Iterable, Any, cast, Callable, Optional, Protocol, Self
import math
from pathlib import Path
import importlib
import os
import os.path
import dataclasses

from PIL import ImageDraw


class _HasIntAdd(Protocol):
    def __add__(self, other: int) -> Self:
        ...


def lerp(a: float, b: float, amount: float) -> float:
    """Linear interpolation between a and b, using amount as the
    interpolation factor. If amount is not between 0 and 1, then this
    function extrapolateslinearly."""
    return a * (1 - amount) + b * amount


def manhattan_circle[X: _HasIntAdd, Y: _HasIntAdd, Z: _HasIntAdd](
        origin: tuple[X, Y, Z],
        distance: int,
) -> Iterator[tuple[X, Y, Z]]:
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


def to_dataclass_checked[T](cls: type[T], value: Any) -> T:
    """Converts the value to an instance of the given dataclass. If
    any of the fields fail to typecheck (to the extent possible at
    runtime in Python), then this function raises an error. If cls is
    not a dataclass, then an error is likewise raised."""
    if not dataclasses.is_dataclass(cls):
        raise TypeError('to_dataclass_checked only works with dataclasses')
    args: dict[str, Any] = {}
    module = importlib.import_module(cls.__module__)
    for field in dataclasses.fields(cls):
        if not field.init:
            continue
        is_required = field.default is dataclasses.MISSING and field.default_factory is dataclasses.MISSING
        try:
            args[field.name] = getattr(value, field.name)
        except AttributeError:
            if is_required:
                raise
        field_type = _parse_dataclass_type(module.__dict__, field.type)
        if not isinstance(args[field.name], field_type):
            raise TypeError(f'Field {field.name} in {cls} (value = {args[field.name]}) is not of type {field.type}')
    return cast(T, cls(**args))


def _parse_dataclass_type(globals: dict[str, Any], type_: str | type[object] | None) -> type[object]:
    if isinstance(type_, type):
        return type_
    if type_ is None:
        return object
    return cast('type[object]', eval(type_, globals))


def project_root() -> Path:
    return Path(__file__).parent.parent.parent


def indexif[T](iterable: Iterable[T], pred: Callable[[T], bool]) -> Optional[int]:
    for i, elem in enumerate(iterable):
        if pred(elem):
            return i
    return None
