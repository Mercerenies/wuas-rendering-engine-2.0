
"""The fire spread mechanics from the 2023 game."""

from __future__ import annotations

from wuas.processing.abc import BoardProcessor
from wuas.board import Board, Space, Attribute
from wuas.config import ConfigFile
from wuas.processing.registry import registered_processor
from wuas.util import manhattan_circle

from typing import Iterable
import random

# I'm not going to pretend this fits into some .json configuration data. I'm
# special-casing the rules.

MCOTW = (-100, -101, -102)

INTRINSICALLY_FIREPROOF = ('start', 'altar', 'water', 'twater', 'ttree')


@registered_processor(aliases=["fire2023"])
class FireSpreadProcessor(BoardProcessor):

    def run(self, config: ConfigFile, board: Board) -> None:
        # Identify all of the current fire spaces.
        fire_spaces = list(_find_fire_spaces(board))
        # Now spread them all.
        for fire_space in fire_spaces:
            _do_fire_spread(board, fire_space)
        # Banish the fire spaces that were here from the start.
        for x, y, z in fire_spaces:
            if z not in MCOTW:
                _banish(board, x, y, z)


def _find_fire_spaces(board: Board) -> Iterable[tuple[int, int, int]]:
    for x, y, z in board.indices:
        if board.get_space(x, y, z).space_name == 'fire':
            yield x, y, z


def _do_fire_spread(board: Board, fire_space: tuple[int, int, int]) -> None:
    distance = 2 if _is_super_fire_space(board, fire_space) else 1
    for x, y, z in manhattan_circle(fire_space, distance):
        if not board.in_bounds(x, y, z):
            continue
        space = board.get_space(x, y, z)
        if not _is_fireproof(space):
            space.space_name = 'fire'


def _is_super_fire_space(board: Board, fire_space: tuple[int, int, int]) -> bool:
    adjacent_spaces = [
        board.get_space(x, y, z).space_name
        for x, y, z in manhattan_circle(fire_space, 1)
        if board.in_bounds(x, y, z)
    ]
    fire_count = adjacent_spaces.count('fire')
    # One of the spaces will always be the current one we're looking
    # at, so if there's more than one, then it's super spreading.
    return fire_count > 1


def _is_fireproof(space: Space) -> bool:
    if Attribute("fireproof") in space.get_attributes():
        return True
    if space.space_name in INTRINSICALLY_FIREPROOF:
        return True
    if 'goldcoin' in [token.token_name for token in space.get_concrete_tokens()]:
        return True
    if space.space_name == 'ash' and 'smolderingimmunity' not in space.attribute_ids:
        return True
    return False


def _banish(board: Board, x: int, y: int, z: int) -> None:
    new_z_choices = [
        floor
        for floor in MCOTW
        if board.in_bounds(x, y, floor) and not _is_fireproof(board.get_space(x, y, floor))
    ]
    board.get_space(x, y, z).space_name = "ash"
    if new_z_choices:
        new_z = random.choice(new_z_choices)
        board.get_space(x, y, new_z).space_name = "fire"
