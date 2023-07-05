
"""Parser for the WUAS datafile format."""

from __future__ import annotations

from wuas.board import Board, TileData, Token, Attribute

from typing import TextIO, NamedTuple
import re


KNOWN_VERSIONS = (1, 2, 3)


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
    elif version in (2, 3):
        # Versions 2 and 3 parse key-value pairs until it hits a newline
        meta = _read_meta(io)

    floors = _read_floors(io, version)
    token_data = _read_tokens(io)
    if version >= 3:
        attr_data = _read_attrs(io)
    else:
        attr_data = {}

    return Board(floors, token_data, attr_data, meta)


def _read_floors(io: TextIO, version: int) -> dict[int, list[list[TileData]]]:
    if version < 3:
        # Versions 1 and 2 don't have floors, so put everything on floor 0.
        board_table = _read_board(io, version)
        return {0: board_table}
    else:
        # The floors of the board
        floors: dict[int, list[list[TileData]]] = {}
        while True:
            header_line = io.readline()
            if header_line == '\n':
                # No more floors, stop reading
                return floors
            if not header_line.startswith("floor="):
                raise RuntimeError(f"Expecting floor number, got '{header_line}'")
            floor_number = int(header_line[6:])
            if floor_number in floors:
                raise RuntimeError(f"Duplicate floor {floor_number}")
            board_table = _read_board(io, version)
            floors[floor_number] = board_table


def _read_board(io: TextIO, version: int) -> list[list[TileData]]:
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
        row = []
        for i in range(len(space_data)):
            space = space_data[i]
            token = token_data[i]
            space_name, attrs = _parse_space(space, version)
            row.append(TileData(space_name, list(token), attrs))
        result.append(row)
    return result


def _split_at_bars(text: str) -> list[str]:
    return text.split('|')[1:-1]


def _read_tokens(io: TextIO) -> dict[str, Token]:
    result = {}
    line = io.readline()
    while line != '' and line != '\n':
        abbreviation, name, item_name, x, y = line.split()
        result[abbreviation] = Token(
            token_name=name,
            item_name=None if item_name == 'nil' else item_name,
            position=(int(x), int(y)),
        )
        line = io.readline()
    return result


def _read_attrs(io: TextIO) -> dict[str, Attribute]:
    result = {}
    line = io.readline()
    while line != '' and line != '\n':
        abbreviation, name = line.split()
        result[abbreviation] = Attribute(name)
        line = io.readline()
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


def _parse_space(space: str, version: int) -> SpaceParseResult:
    if version < 3:
        # Versions 1 and 2 of the API have an ad-hoc rule that removes
        # stars and question marks. They do NOT have attributes.
        space = space.replace("*", "").replace("?", "")
        return SpaceParseResult(space, [])
    else:
        # The space's proper name is a sequence of alphanumeric
        # characters. Anything else is an attribute reference.
        m = re.match(r"^([A-Za-z]+)(.*)$", space)
        assert m
        return SpaceParseResult(m[1], list(m[2]))


class SpaceParseResult(NamedTuple):
    space_name: str
    attributes: list[str]
