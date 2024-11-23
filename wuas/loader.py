
"""Parser for the WUAS datafile format."""

from __future__ import annotations

from wuas.board import Board, TileData, Token, Attribute, HiddenToken, ConcreteToken
from wuas.graph import GraphEdge

from typing import TextIO, NamedTuple
import re


KNOWN_VERSIONS = (1, 2, 3, 4, 5)

SPACE_LABEL_MARKER = '&'


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
    else:
        # Versions > 1 parse key-value pairs until it hits a newline
        meta = _read_meta(io)

    floors = _read_floors(io, version)
    token_data = _read_tokens(io, version)

    if version >= 3:
        attr_data = _read_attrs(io)
    else:
        attr_data = {}

    if version >= 4:
        graph_data = _read_graph(io)
    else:
        graph_data = []

    return Board(floors, token_data, attr_data, meta, graph_data)


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
            token = list(token_data[i])
            space_name, attrs = _parse_space(space, version)
            tile_data = TileData(space_name, token, attrs)
            if version >= 4:
                # Version >= 4 parses space labels. Lower versions
                # never have them.
                _read_space_label(token, tile_data)
            row.append(tile_data)
        result.append(row)
    return result


def _read_space_label(token_list: list[str], tile_data: TileData) -> None:
    try:
        index = token_list.index(SPACE_LABEL_MARKER)
    except ValueError:
        # No label, so don't do anything
        return
    label = token_list[index + 1]
    token_list[index:index + 2] = []
    tile_data.space_label = label


def _split_at_bars(text: str) -> list[str]:
    return text.split('|')[1:-1]


def _read_tokens(io: TextIO, version: int) -> dict[str, Token]:
    result: dict[str, Token] = {}
    line = io.readline()
    while line != '' and line != '\n':
        abbreviation, name, item_name, x, y = line.split()
        if abbreviation == SPACE_LABEL_MARKER and version >= 4:
            raise ValueError("'&' is an invalid token abbreviation")
        if version >= 5 and HiddenToken.is_hidden_name(name):
            # Versions >= 5 support the "hidden" token marker
            _assert_valid_hidden_token(item_name, x, y)
            result[abbreviation] = HiddenToken(full_name=name)
        else:
            result[abbreviation] = ConcreteToken(
                token_name=name,
                item_name=None if item_name == 'nil' else item_name,
                position=(int(x), int(y)),
            )
        line = io.readline()
    return result


def _assert_valid_hidden_token(item_name: str, x: str, y: str) -> None:
    if item_name != 'nil' or x != '0' or y != '0':
        raise ValueError(f"Invalid hidden token: {item_name} {x} {y}")


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


def _read_graph(io: TextIO) -> list[GraphEdge]:
    result = []
    line = io.readline()
    while line != '' and line != '\n':
        result.append(GraphEdge.parse_from_line(line.strip()))
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
        if space == '':
            return SpaceParseResult('', [])
        else:
            m = re.match(r"^([A-Za-z]+)(.*)$", space)
            assert m
            return SpaceParseResult(m[1], list(m[2]))


class SpaceParseResult(NamedTuple):
    space_name: str
    attributes: list[str]
