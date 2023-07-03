
"""Parser for the WUAS datafile format."""

from __future__ import annotations

from wuas.board import Board, TileData, Token

from typing import TextIO
import re


KNOWN_VERSIONS = (1, 2)


def load_from_file(filename: str) -> Board:
    with open(filename, 'r') as input_file:
        return load_from_io(input_file)


def load_from_io(io: TextIO) -> Board:
    # Ignore leading comments and the blank line after them.
    while io.readline().startswith("#"):
        pass

    # Version number
    version = int(io.readline())
    if version not in KNOWN_VERSIONS:
        raise RuntimeError(f"Invalid version number {version}")

    if version == 1:
        # Version 1 parses no metadata
        meta = {}
    elif version == 2:
        # Version 2 parses key-value pairs until it hits a newline
        meta = _read_meta(io)

    # The board text itself
    board_table = _read_board(io)

    # Tile reference data
    token_data = _read_tokens(io)

    return Board(board_table, token_data, meta)


def _read_board(io: TextIO) -> list[list[TileData]]:
    result = []
    while True:
        io.readline()  # Ignore the header
        space_row = io.readline()
        if '|' not in space_row:
            # This is the blank line after the end, so stop reading
            # the board.
            break
        space_data = [space.strip() for space in _split_at_bars(space_row)]
        token_data = [token.strip() for token in _split_at_bars(io.readline())]
        assert len(space_data) == len(token_data)
        result.append([TileData(space_name, list(token)) for space_name, token in zip(space_data, token_data)])
    return result


def _split_at_bars(text: str) -> list[str]:
    return text.split('|')[1:-1]


def _read_tokens(io: TextIO) -> dict[str, Token]:
    result = {}
    while line := io.readline():
        abbreviation, name, item_name, x, y = line.split()
        result[abbreviation] = Token(
            token_name=name,
            item_name=None if item_name == 'nil' else item_name,
            position=(int(x), int(y)),
        )
    return result


def _read_meta(io: TextIO) -> dict[str, str]:
    result = {}
    line = io.readline()
    while line != '\n':
        line = line.strip()
        key, value = re.split(r":\s*", line)
        result[key] = value
        line = io.readline()
    return result
