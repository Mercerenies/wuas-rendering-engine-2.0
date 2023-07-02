
from __future__ import annotations

from wuas.board import Board
from wuas.config import normalize_space_name
from wuas.constants import SPACE_WIDTH, SPACE_HEIGHT

from typing import TypedDict, TypeAlias

WuasJsonOutput: TypeAlias = 'dict[str, Floor]'


class Floor(TypedDict):
    spaces: list[list[str]]
    tokens: list[Token]


class Token(TypedDict):
    object: str
    position: tuple[int, int]


def render_to_json(board: Board) -> WuasJsonOutput:
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
