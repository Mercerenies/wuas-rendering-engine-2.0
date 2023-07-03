
"""Rendering functions which output JSON in a format compatible with the
WUAS interactive web UI."""

from __future__ import annotations

from wuas.board import Board
from wuas.config import ConfigFile, normalize_space_name
from wuas.constants import SPACE_WIDTH, SPACE_HEIGHT
from wuas.output.abc import OutputProducer

import sys
import json
from typing import TypedDict, TypeAlias, TextIO

WuasJsonOutput: TypeAlias = 'dict[str, Floor]'


class Floor(TypedDict):
    spaces: list[list[str]]
    tokens: list[Token]


class Token(TypedDict):
    object: str
    position: tuple[int, int]


def render_to_json(board: Board) -> WuasJsonOutput:
    """Return a JSON-like structure representing the board in a way
    compatible with the WUAS web UI."""
    spaces = _render_spaces(board)
    tokens = _render_tokens(board)

    return {
        '0': {'spaces': spaces, 'tokens': tokens},
    }


def _render_spaces(board: Board) -> list[list[str]]:
    spaces = []
    for y in range(board.height):
        row = []
        for x in range(board.width):
            current_space = board.get_space(x, y)
            row.append(normalize_space_name(current_space.space_name))
        spaces.append(row)
    return spaces


def _render_tokens(board: Board) -> list[Token]:
    tokens: list[Token] = []
    for x, y in board.indices:
        current_space = board.get_space(x, y)
        for token in current_space.get_tokens():
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

    def produce_output(self, config: ConfigFile, board: Board) -> None:
        json_data = render_to_json(board)
        json.dump(json_data, self._io)
        self._io.write('\n')
