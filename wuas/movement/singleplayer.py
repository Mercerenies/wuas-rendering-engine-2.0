
from __future__ import annotations

from wuas.board import Board, move_token


class SinglePlayerBoard:
    """A board, as viewed by a particular player token.

    Invariant: The player targeted by this board must only be moved
    through the methods defined on this class. Other modifications may
    be made to the board through the Board class, provided that those
    modifications do not move this particular player.

    """
    board: Board
    _player_pos: tuple[int, int, int]
    player_id: str

    def __init__(self, board: Board, player_pos: tuple[int, int, int], player_id: str) -> None:
        """Constructs a SinglePlayerBoard by zooming in on a
        particular player of a Board object. If the target player is
        not at the indicated position, then this constructor raises
        ValueError.

        """
        self.board = board
        self._player_pos = player_pos
        self.player_id = player_id

        space = self.board.get_space(self.player_pos)
        if not any(token.name == self.player_id for token in space.get_tokens()):
            raise ValueError("Target player is not at indicated position")

    @property
    def player_pos(self) -> tuple[int, int, int]:
        """The position of the player targeted by this board."""
        return self._player_pos

    @player_pos.setter
    def player_pos(self, pos: tuple[int, int, int]) -> None:
        """Moves the player targeted by this board to the indicated
        position."""
        move_token(self.board, token_id=self.player_id, src=self.player_pos, dest=pos)
        self._player_pos = pos

    def move_player(self, delta: tuple[int, int, int]) -> tuple[int, int, int]:
        """Moves the player targeted by this board by the indicated
        amount."""
        self.player_pos = _add_tuple3(self.player_pos, delta)
        return self.player_pos


# TODO: This should REALLY be a Vector3 (and corresponding Vector2)
# class everywhere, rather than doing this nonsense.
def _add_tuple3(a: tuple[int, int, int], b: tuple[int, int, int], /) -> tuple[int, int, int]:
    """Adds two 3-tuples."""
    ax, ay, az = a
    bx, by, bz = b
    return (ax + bx, ay + by, az + bz)
