
"""Rendering functions which output JSON in a format compatible with the
WUAS interactive web UI."""

from __future__ import annotations

from wuas.board import Board, Floor, Space
from wuas.config import ConfigFile, normalize_space_name
from wuas.constants import SPACE_WIDTH, SPACE_HEIGHT
from wuas.output.abc import OutputProducer, OutputArgs
from wuas.output.registry import REGISTERED_PRODUCERS

import sys
import json
from typing import TypedDict, TypeAlias, TextIO

WuasJsonOutput: TypeAlias = 'dict[str, FloorData]'
SpaceData: TypeAlias = 'str | ExpandedSpaceData'


class FloorData(TypedDict):
    spaces: list[list[SpaceData]]
    tokens: list[Token]


class ExpandedSpaceData(TypedDict):
    """Spaces can be simple strings if they have no attributes. If
    they have attributes, then the expanded form consists of this
    dictionary."""
    space: str
    attributes: list[str]


class Token(TypedDict):
    object: str
    position: tuple[int, int]


def render_to_json(config: ConfigFile, board: Board) -> WuasJsonOutput:
    """Return a JSON-like structure representing the board in a way
    compatible with the WUAS web UI."""
    result: WuasJsonOutput = {}
    for z, floor in board.floors.items():
        spaces = _render_spaces(config, floor)
        tokens = _render_tokens(floor)
        result[str(z)] = {'spaces': spaces, 'tokens': tokens}
    return result


def _render_spaces(config: ConfigFile, floor: Floor) -> list[list[SpaceData]]:
    spaces = []
    for y in range(floor.height):
        row = []
        for x in range(floor.width):
            current_space = floor.get_space(x, y)
            space_name = _determine_space_name(config, current_space)
            space_data: SpaceData
            if current_space.get_attributes():
                space_data = {
                    "space": normalize_space_name(space_name),
                    "attributes": [attr.name for attr in current_space.get_attributes()],
                }
            else:
                space_data = normalize_space_name(space_name)
            row.append(space_data)
        spaces.append(row)
    return spaces


def _determine_space_name(config: ConfigFile, current_space: Space) -> str:
    # Resolve the actual effect name if this is a rendered composite
    # space. Otherwise, leave it alone.
    try:
        composite_space_data = config.definitions.get_composite_space(current_space.space_name)
        return composite_space_data.effect
    except KeyError:
        return current_space.space_name


def _render_tokens(floor: Floor) -> list[Token]:
    tokens: list[Token] = []
    for x, y in floor.indices:
        current_space = floor.get_space(x, y)
        for token in current_space.get_concrete_tokens():
            object_name = token.item_name if token.item_name is not None else token.token_name
            dx, dy = token.position
            tokens.append({
                "object": object_name,
                "position": (x * SPACE_WIDTH + dx, y * SPACE_HEIGHT + dy),
            })
    return tokens


class JsonProducer(OutputProducer):
    """Dumps the board, as JSON, to the given I/O object."""

    _io: TextIO

    def __init__(self, io: TextIO) -> None:
        self._io = io

    @classmethod
    def stdout(cls) -> JsonProducer:
        """JsonProducer which outputs to sys.stdout."""
        return cls(sys.stdout)

    def produce_output(self, config: ConfigFile, board: Board, args: OutputArgs) -> None:
        args.assert_no_args()
        json_data = render_to_json(config, board)
        json.dump(json_data, self._io)
        self._io.write('\n')


REGISTERED_PRODUCERS.register_callable('json', JsonProducer.stdout)
