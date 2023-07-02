
from __future__ import annotations

from wuas.board import Board, Space, TileData, Token, BoardIntegrityError
from wuas.config import ConfigFile


class ValidationError(Exception):
    pass


def validate(config: ConfigFile, board: Board) -> None:
    definitions = config.definitions
    for x, y in board.indices:
        try:
            space = board.get_space(x, y)
        except BoardIntegrityError as exc:
            raise ValidationError("Integrity error in the board .dat file") from exc
        # Verify that the space and any tokens/items on it actually
        # exist.
        if not definitions.has_space(space.space_name):
            raise ValidationError(f"No such space {space.space_name}")
        for token_data in space.get_tokens():
            if not definitions.has_token(token_data.token_name):
                raise ValidationError(f"No such token {token_data.token_name}")
            if token_data.item_name and not definitions.has_item(token_data.item_name):
                raise ValidationError(f"No such item {token_data.item_name}")