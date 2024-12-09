
"""This module supplies the main Board class, which stores a mutable
WUAS board."""

from __future__ import annotations

from wuas.config import normalize_space_name
from wuas.graph import GraphEdge
from wuas.util import indexif

from dataclasses import dataclass
from typing import Mapping, Sequence, Iterator, Union, overload
from functools import cached_property


class Board:
    """The board object itself, which contains a two-dimensional grid of
    spaces, an ordered mapping of abbreviations to tokens and items, and
    a mapping of keys to arbitrary string metadata.

    Invariant: All floors have the same width and height."""

    _floors: dict[int, list[list[TileData]]]
    _references: dict[str, Token]
    _attributes: dict[str, Attribute]
    # Meta data, included after the version number as a set of
    # key-value pairs.
    _meta: dict[str, str]
    # Graph data, for highway-like interactions.
    _graph_edges: list[GraphEdge]

    # TODO I don't like the complex type of floor_map
    def __init__(self,
                 floor_map: dict[int, list[list[TileData]]],
                 references: dict[str, Token],
                 attributes: dict[str, Attribute],
                 meta: dict[str, str],
                 graph_edges: list[GraphEdge]) -> None:
        """Construct a board consisting of the given floors. All floors
        must have the same dimensions. This invariant is checked at
        construction time."""
        self._floors = floor_map
        self._references = references
        self._attributes = attributes
        self._meta = meta
        self._graph_edges = graph_edges
        # Check that all floors have the same width and height
        if self._floors:
            first_floor = Floor(next(iter(self._floors.values())), references, attributes)
            width = first_floor.width
            height = first_floor.height
            for key, floor_grid in self._floors.items():
                floor = Floor(floor_grid, references, attributes)
                if (floor.width, floor.height) != (width, height):
                    raise BoardIntegrityError(f"Floor {key} has inconsistent width/height")

    @property
    def tokens(self) -> Mapping[str, Token]:
        """The mapping from abbreviations to token objects."""
        return self._references

    @property
    def attributes(self) -> Mapping[str, Attribute]:
        """The mapping from abbreviations to attribute objects."""
        return self._attributes

    @property
    def floors(self) -> Mapping[int, Floor]:
        return _FloorMapping(self._floors, self._references, self._attributes)

    @overload
    def get_space(self, x: int, y: int, z: int, /) -> Space:
        ...

    @overload
    def get_space(self, pos: tuple[int, int, int], /) -> Space:
        ...

    def get_space(self, x_or_pos: int | tuple[int, int, int], y: int | None = None, z: int | None = None, /) -> Space:
        """Return the space at the given position. This is a live view,
        so mutations to the returned Space object will affect this Board
        in real time. Raises IndexError if out of bounds."""
        if isinstance(x_or_pos, tuple):
            return self.get_space(*x_or_pos)
        x = x_or_pos
        assert isinstance(y, int)
        assert isinstance(z, int)
        if self.in_bounds(x, y, z):
            return self.floors[z].get_space(x, y)
        else:
            raise IndexError(f"Position {(x, y, z)} out of bounds in board of size {(self.width, self.height)}")

    @property
    def indices(self) -> Iterator[tuple[int, int, int]]:
        for z, floor in sorted(self.floors.items(), key=lambda x: x[0]):
            for x, y in floor.indices:
                yield x, y, z

    @property
    def height(self) -> int:
        """The height of the board."""
        if self.floors:
            floor = next(iter(self.floors.values()))
            return floor.height
        else:
            return 0

    @property
    def width(self) -> int:
        """The width of the board."""
        if self.floors:
            floor = next(iter(self.floors.values()))
            return floor.width
        else:
            return 0

    def resize(self, new_left: int, new_top: int, new_right: int, new_bottom: int, initial_value: str) -> None:
        """Expand each floor of the board in each direction by the given
        amount. The four integer arguments must be nonnegative.
        initial_value specifies the space type to put in the new
        positions. Each new position created in this way will initially
        have no tokens or items on it."""
        for floor in self.floors.values():
            floor.resize_unsafe(new_left, new_top, new_right, new_bottom, initial_value)

    def in_bounds(self, x: int, y: int, z: int) -> bool:
        """Returns whether or not the given 0-based position in within
        the board's current bounds."""
        if z not in self._floors:
            return False
        return 0 <= x < self.width and 0 <= y < self.height

    def has_meta(self, key: str) -> bool:
        """Returns whether the key exists in this object's metadata table.
        Equivalent to `key in self.meta`"""
        return key in self._meta

    def get_meta(self, key: str) -> str:
        """Returns the metadata for the given key. Raises KeyError if it
        doesn't exist. Equivalent to `self.meta[key]`"""
        return self._meta[key]

    @property
    def meta(self) -> Mapping[str, str]:
        """The metadata mapping."""
        return self._meta

    @property
    def graph_edges(self) -> Sequence[GraphEdge]:
        """The graph edges present on the board."""
        return self._graph_edges

    @cached_property
    def labels_map(self) -> Mapping[str, tuple[int, int, int]]:
        """A mapping from space labels to their 0-based coordinates."""
        result = {}
        for x, y, z in self.indices:
            space = self.get_space(x, y, z)
            if space.space_label:
                result[space.space_label] = (x, y, z)
        return result

    def recompute_labels_map(self) -> None:
        """Clears the cache on labels_map. Should be called whenever
        an effect moves a space that might have a label."""
        try:
            del self.labels_map
        except AttributeError:
            # Has not been initialized yet, so nothing to do.
            pass


class Floor:
    """A floor of the board, which contains a two-dimensional grid of spaces
    and an ordered mapping of abbreviations to tokens and items.

    This is a live reference to the Board, and modifications will affect
    the board in real-time."""

    # Board data is stored in row-major order.
    _data: list[list[TileData]]
    _references: dict[str, Token]
    _attributes: dict[str, Attribute]

    def __init__(self,
                 data: list[list[TileData]],
                 references: dict[str, Token],
                 attributes: dict[str, Attribute]) -> None:
        self._data = data
        self._references = references
        self._attributes = attributes

    def in_bounds(self, x: int, y: int) -> bool:
        """Returns whether or not the given 0-based position in within
        the floor's current bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    @property
    def height(self) -> int:
        """The height of the floor."""
        return len(self._data)

    @property
    def width(self) -> int:
        """The width of the floor. If the floor has zero height, then it
        will necessarily have zero width as well, due to the way
        boards are stored internally."""
        if self.height == 0:
            return 0
        else:
            return len(self._data[0])

    def resize_unsafe(self, new_left: int, new_top: int, new_right: int, new_bottom: int, initial_value: str) -> None:
        """Expand the floor in each direction by the given amount. The
        four integer arguments must be nonnegative. initial_value
        specifies the space type to put in the new positions. Each new
        position created in this way will initially have no tokens or
        items on it.

        Note: This function is marked unsafe. You should use Board.resize,
        which calls this function and enforces the invariant that all floors
        have the same dimensions, instead of calling this function directly."""

        # Left and Right
        for y in range(self.height):
            left = [TileData(initial_value, [], []) for _ in range(new_left)]
            right = [TileData(initial_value, [], []) for _ in range(new_right)]
            self._data[y] = left + self._data[y] + right
        # Top
        for _ in range(new_top):
            self._data.insert(0, [TileData(initial_value, [], []) for _ in range(self.width)])
        # Bottom
        for _ in range(new_bottom):
            self._data.append([TileData(initial_value, [], []) for _ in range(self.width)])

    def get_space(self, x: int, y: int) -> Space:
        """Return the space at the given position. This is a live view,
        so mutations to the returned Space object will affect this Board
        in real time. Raises IndexError if out of bounds."""
        if self.in_bounds(x, y):
            return Space(self._data[y][x], self._references, self._attributes)
        else:
            raise IndexError(f"Position {(x, y)} out of bounds in board of size {(self.width, self.height)}")

    @property
    def indices(self) -> Iterator[tuple[int, int]]:
        """All of the indices of this board. This property produces
        elements of the form (x, y) in row-major order (so all of the
        y=0 positions will be produced before any of the y=1 ones)."""
        for y in range(0, self.height):
            for x in range(0, self.width):
                yield (x, y)

    @property
    def tiles(self) -> TileMapping:
        """The mapping from (x, y) coordinates to TileData objects."""
        return TileMapping(self, self._data)


class TileMapping:
    _floor: Floor
    _tiles: list[list[TileData]]

    def __init__(self, floor: Floor, tiles: list[list[TileData]]) -> None:
        self._floor = floor
        self._tiles = tiles

    def __getitem__(self, tup: tuple[int, int]) -> TileData:
        x, y = tup
        try:
            return self._tiles[y][x]
        except IndexError:
            raise IndexError(
                f"Position {(x, y)} out of bounds in board of size {(self._floor.width, self._floor.height)}"
            ) from None

    def __setitem__(self, tup: tuple[int, int], value: TileData) -> None:
        x, y = tup
        try:
            self._tiles[y][x] = value
        except IndexError:
            raise IndexError(
                f"Position {(x, y)} out of bounds in board of size {(self._floor.width, self._floor.height)}"
            ) from None

    def __iter__(self) -> Iterator[tuple[int, int]]:
        return self._floor.indices

    def __len__(self) -> int:
        return self._floor.height * self._floor.width


class _FloorMapping(Mapping[int, Floor]):
    _floors: dict[int, list[list[TileData]]]
    _references: dict[str, Token]
    _attributes: dict[str, Attribute]

    def __init__(self,
                 floors: dict[int, list[list[TileData]]],
                 references: dict[str, Token],
                 attributes: dict[str, Attribute]) -> None:
        self._floors = floors
        self._references = references
        self._attributes = attributes

    def __getitem__(self, floor_index: int) -> Floor:
        tile_grid = self._floors[floor_index]
        return Floor(tile_grid, self._references, self._attributes)

    def __iter__(self) -> Iterator[int]:
        return iter(self._floors)

    def __len__(self) -> int:
        return len(self._floors)


@dataclass
class TileData:
    """The data about a particular tile. Note that users outside the
    module should generally not need to interact with this class and
    will instead use the Space class, which abstracts away the
    details of the token IDs."""
    space_name: str
    token_ids: list[str]
    attribute_ids: list[str]
    space_label: str | None = None


class Space:
    """A space on the board, consisting of a space type and zero or
    more tokens. This is a live reference to a Board, and changes to
    the space mutate the board in-place."""
    _tile_data: TileData
    _references: Mapping[str, Token]
    _attributes: Mapping[str, Attribute]

    def __init__(self,
                 tile_data: TileData,
                 references: Mapping[str, Token],
                 attributes: Mapping[str, Attribute]) -> None:
        self._tile_data = tile_data
        self._references = references
        self._attributes = attributes

    @property
    def space_name(self) -> str:
        """The name of the space's type."""
        return normalize_space_name(self._tile_data.space_name)

    @space_name.setter
    def space_name(self, value: str) -> None:
        self._tile_data.space_name = value

    @property
    def space_label(self) -> str | None:
        """A unique label identifying the space on the board. If
        present, this label must be globally unique."""
        return self._tile_data.space_label

    @space_label.setter
    def space_label(self, value: str | None) -> None:
        self._tile_data.space_label = value

    @property
    def token_ids(self) -> Sequence[str]:
        """The string abbreviations for the tokens on this space. All
        tokens listed here must be keys in board.tokens. If this
        sequence is set to a value which does not satisfy that
        constraint, an AssertionError will be raised.

        For uses that do not need to mutate the tokens, consider
        get_tokens(), which returns a wrapped object containing more
        information than just the abbreviation."""
        return self._tile_data.token_ids

    @token_ids.setter
    def token_ids(self, sequence: Sequence[str]) -> None:
        # Check that they make sense
        for token_id in sequence:
            assert token_id in self._references
        # Then assign to the tile data
        self._tile_data.token_ids = list(sequence)

    def append_token_id(self, new_token_id: str) -> None:
        """Equivalent to the following, but faster since this avoids
        allocating the intermediate list.

        ```
        tokens = list(self.token_ids)
        tokens.append(new_token_id)
        self.token_ids = tokens
        ```
        """
        assert new_token_id in self._references
        self._tile_data.token_ids.append(new_token_id)

    @property
    def attribute_ids(self) -> Sequence[str]:
        """The string abbreviations for the attributes on this space.
        All attributes listed here must be keys in board.attributes.
        If this sequence is set to a value which does not satisfy that
        constraint, an AssertionError will be raised.

        For uses that do not need to mutate the sequence, consider
        get_attributes(), which returns a wrapped object containing
        more information than just the abbreviation.

        """
        return self._tile_data.attribute_ids

    @attribute_ids.setter
    def attribute_ids(self, sequence: Sequence[str]) -> None:
        # Check that they make sense
        for attr_id in sequence:
            assert attr_id in self._attributes
        # Then assign to the tile data
        self._tile_data.attribute_ids = list(sequence)

    def get_tokens(self) -> Sequence[Token]:
        """Returns an ordered sequence of the tokens on this space."""
        try:
            return [self._references[token_id] for token_id in self._tile_data.token_ids]
        except KeyError as exc:
            raise BoardIntegrityError(f"No such token {str(exc)} in references table")

    def get_concrete_tokens(self) -> Sequence[ConcreteToken]:
        """Returns an ordered sequence of all tokens on this space,
        with HiddenTokens removed."""
        return [ct for ct in self.get_tokens() if isinstance(ct, ConcreteToken)]

    def get_attributes(self) -> Sequence[Attribute]:
        """Returns an ordered sequence of the attribues on this
        space."""
        try:
            return [self._attributes[attr_id] for attr_id in self._tile_data.attribute_ids]
        except KeyError as exc:
            raise BoardIntegrityError(f"No such attribute {str(exc)} in references table")


Token = Union['ConcreteToken', 'HiddenToken']


@dataclass(frozen=True)
class ConcreteToken:
    """A token on a given space."""
    token_name: str
    item_name: str | None
    # (x, y) relative to the top-left corner of the space.
    position: tuple[int, int]

    @property
    def name(self) -> str:
        return self.token_name


@dataclass(frozen=True)
class HiddenToken:
    """Class representing a hidden token that does NOT get rendered.
    These do NOT show up in the JSON or image outputs, but do show up
    in the datafile output.

    Hidden tokens should be used for internal documentation purposes,
    specifically for things that the players should not see.

    """
    full_name: str

    NAME_SUFFIX: str = '_HIDDEN'

    @property
    def name(self) -> str:
        if self.full_name.endswith(self.NAME_SUFFIX):
            return self.full_name[:-len(self.NAME_SUFFIX)]
        else:
            return self.full_name

    @classmethod
    def is_hidden_name(cls, name: str) -> bool:
        return name.endswith(cls.NAME_SUFFIX)

    def to_concrete(self) -> ConcreteToken:
        """Explicit cast to a concrete token which will parse as this
        hidden token."""
        return ConcreteToken(self.full_name, None, (0, 0))


@dataclass(frozen=True)
class Attribute:
    """A space-level attribute."""
    name: str


class BoardIntegrityError(Exception):
    pass


def move_token(
        board: Board,
        token_id: str,
        src: tuple[int, int, int],
        dest: tuple[int, int, int] | None,
) -> None:
    """Moves one instance of the token from the source to the
    destination. Throws ValueError if no instances of that token exist
    at that position.

    If dest is None, then the token is removed from play rather than
    being moved.

    """
    token_refs = [ref for ref, token in board.tokens.items() if token.name == token_id]
    src_token_ids = list(board.get_space(*src).token_ids)
    matching_index = indexif(src_token_ids, lambda ref: ref in token_refs)
    if matching_index is None:
        raise ValueError(f"No instances of token {token_id} at position {src}")
    matching_id = src_token_ids[matching_index]
    del src_token_ids[matching_index]
    board.get_space(*src).token_ids = src_token_ids
    if dest is not None:
        board.get_space(*dest).append_token_id(matching_id)


def delete_token(board: Board, token_id: str, src: tuple[int, int, int]) -> None:
    """Removes one instance of the token from the source. Throws
    ValueError if no instances of that token exist at that position.

    Equivalent to move_token with a dest argument of None.

    """
    move_token(board, token_id, src, dest=None)
