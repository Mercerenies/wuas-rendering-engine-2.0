
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence, Iterable


class Board:
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
        return len(self._data)

    @property
    def width(self) -> int:
        if self.height == 0:
            return 0
        else:
            return len(self._data[0])

    def resize(self, new_left: int, new_top: int, new_right: int, new_bottom: int, initial_value: str) -> None:
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
        return 0 <= x < self.width and 0 <= y < self.height

    # Returns a mutable object, to which changes affect the game board
    # itself.
    def get_space(self, x: int, y: int) -> Space:
        if self.in_bounds(x, y):
            return Space(self._data[y][x], self._references)
        else:
            raise IndexError(f"Position {(x, y)} out of bounds in board of size {(self.width, self.height)}")

    def has_meta(self, key: str) -> bool:
        return key in self._meta

    def get_meta(self, key: str) -> str:
        return self._meta[key]

    @property
    def meta(self) -> Mapping[str, str]:
        return self._meta

    @property
    def tokens(self) -> Mapping[str, Token]:
        return self._references

    @property
    def indices(self) -> Iterable[tuple[int, int]]:
        for y in range(0, self.height):
            for x in range(0, self.width):
                yield (x, y)


@dataclass
class TileData:
    space_name: str
    token_ids: list[str]


class Space:
    _tile_data: TileData
    _references: Mapping[str, Token]

    def __init__(self, tile_data: TileData, references: Mapping[str, Token]) -> None:
        self._tile_data = tile_data
        self._references = references

    @property
    def space_name(self) -> str:
        return self._tile_data.space_name

    @space_name.setter
    def space_name(self, value: str) -> None:
        self._tile_data.space_name = value

    @property
    def token_ids(self) -> Sequence[str]:
        return self._tile_data.token_ids

    @token_ids.setter
    def token_ids(self, sequence: Sequence[str]) -> None:
        # Check that they make sense
        for token_id in sequence:
            assert token_id in self._references
        # Then assign to the tile data
        self._tile_data.token_ids = list(sequence)

    def get_tokens(self) -> Sequence[Token]:
        try:
            return [self._references[token_id] for token_id in self._tile_data.token_ids]
        except KeyError as exc:
            raise BoardIntegrityError(f"No such token {str(exc)} in references table")


@dataclass(frozen=True)
class Token:
    token_name: str
    item_name: str | None
    # (x, y) relative to the top-left corner of the space.
    position: tuple[int, int]


class BoardIntegrityError(Exception):
    pass
