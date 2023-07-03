
"""This module supplies the main Board class, which stores a mutable
WUAS board."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence, Iterable


class Board:
    """The board object itself, which contains a two-dimensional grid of
    spaces, an ordered mapping of abbreviations to tokens and items, and
    a mapping of keys to arbitrary string metadata."""

    # Board data is stored in row-major order.
    _data: list[list[TileData]]
    _references: dict[str, Token]
    # Meta data, included after the version number as a set of
    # key-value pairs.
    _meta: dict[str, str]

    def __init__(self, data: list[list[TileData]], references: dict[str, Token], meta: dict[str, str]) -> None:
        self._data = data
        self._references = references
        self._meta = meta

    @property
    def height(self) -> int:
        """The height of the board."""
        return len(self._data)

    @property
    def width(self) -> int:
        """The width of the board. If the board has zero height, then it
        will necessarily have zero width as well, due to the way boards
        are stored internally.."""
        if self.height == 0:
            return 0
        else:
            return len(self._data[0])

    def resize(self, new_left: int, new_top: int, new_right: int, new_bottom: int, initial_value: str) -> None:
        """Expand the board in each direction by the given amount. The
        four integer arguments must be nonnegative. initial_value
        specifies the space type to put in the new positions. Each new
        position created in this way will initially have no tokens or
        items on it."""

        # Left and Right
        for y in range(self.height):
            left = [TileData(initial_value, []) for _ in range(new_left)]
            right = [TileData(initial_value, []) for _ in range(new_right)]
            self._data[y] = left + self._data[y] + right
        # Top
        for _ in range(new_top):
            self._data.insert(0, [TileData(initial_value, []) for _ in range(self.width)])
        # Bottom
        for _ in range(new_bottom):
            self._data.append([TileData(initial_value, []) for _ in range(self.width)])

    def in_bounds(self, x: int, y: int) -> bool:
        """Returns whether or not the given 0-based position in within
        the board's current bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_space(self, x: int, y: int) -> Space:
        """Return the space at the given position. This is a live view,
        so mutations to the returned Space object will affect this Board
        in real time. Raises IndexError if out of bounds."""
        if self.in_bounds(x, y):
            return Space(self._data[y][x], self._references)
        else:
            raise IndexError(f"Position {(x, y)} out of bounds in board of size {(self.width, self.height)}")

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
    def tokens(self) -> Mapping[str, Token]:
        """The mapping from abbreviations to token objects."""
        return self._references

    @property
    def indices(self) -> Iterable[tuple[int, int]]:
        """All of the indices of this board. This property produces
        elements of the form (x, y) in row-major order (so all of the
        y=0 positions will be produced before any of the y=1 ones)."""
        for y in range(0, self.height):
            for x in range(0, self.width):
                yield (x, y)


@dataclass
class TileData:
    """The data about a particular tile. Note that users outside the
    module should generally not need to interact with this class and
    will instead use the Space class, which abstracts away the
    details of the token IDs."""
    space_name: str
    token_ids: list[str]


class Space:
    """A space on the board, consisting of a space type and zero or
    more tokens. This is a live reference to a Board, and changes to
    the space mutate the board in-place."""
    _tile_data: TileData
    _references: Mapping[str, Token]

    def __init__(self, tile_data: TileData, references: Mapping[str, Token]) -> None:
        self._tile_data = tile_data
        self._references = references

    @property
    def space_name(self) -> str:
        """The name of the space's type."""
        return self._tile_data.space_name

    @space_name.setter
    def space_name(self, value: str) -> None:
        self._tile_data.space_name = value

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

    def get_tokens(self) -> Sequence[Token]:
        """Returns an ordered sequence of the tokens on this space."""
        try:
            return [self._references[token_id] for token_id in self._tile_data.token_ids]
        except KeyError as exc:
            raise BoardIntegrityError(f"No such token {str(exc)} in references table")


@dataclass(frozen=True)
class Token:
    """A token on a given space."""
    token_name: str
    item_name: str | None
    # (x, y) relative to the top-left corner of the space.
    position: tuple[int, int]


class BoardIntegrityError(Exception):
    pass
