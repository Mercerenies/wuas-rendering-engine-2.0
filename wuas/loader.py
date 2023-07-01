
from __future__ import annotations

from wuas.board import Board, Space, TileData, Token

from typing import TextIO


def load_from_file(filename: str) -> Board:
    with open(filename, 'r') as input_file:
        return load_from_io(input_file)


def load_from_io(io: TextIO) -> Board:
    # Ignore leading comments and the blank line after them.
    while io.readline().startswith("#"):
        pass

    # Version number (must be equal to one)
    version = int(io.readline())
    if version != 1:
        raise RuntimeError(f"Invalid version number {version}")

    # The board text itself
    board_table = _read_board(io)

    # Tile reference data
    token_data = _read_tokens(io)

    return Board(board_table, token_data)


def _read_board(io: TextIO) -> list[list[TileData]]:
    result = []
    while True:
        io.readline() # Ignore the header
        space_row = io.readline()
        if '|' not in space_row:
            # This is the blank line after the end, so stop reading
            # the board.
            break
        space_data = [space.strip() for space in space_row.split('|')]
        token_data = [token.strip() for token in io.readline().split('|')]
        assert len(space_data) == len(token_data)
        result.append([TileData(space_name, list(token)) for space_name, token in zip(space_data, token_data)])
    return result


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
