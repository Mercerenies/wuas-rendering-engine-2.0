
"""Board processor which mirrors the board horizontally. Simplified
version of game2024_mirror, which also attempts to preserve player
locations."""

from __future__ import annotations

from wuas.processing.abc import BoardProcessor
from wuas.board import Board, Floor, ConcreteToken
from wuas.config import ConfigFile
from wuas.processing.registry import registered_processor


_DEFAULT_SPAN = (1, 1)


@registered_processor(aliases=["mirror"])
class MirrorProcessor(BoardProcessor):

    def run(self, config: ConfigFile, board: Board) -> None:
        for floor in board.floors.values():
            self._mirror_floor(floor)
            self._adjust_tokens(config, board, floor)
        board.recompute_labels_map()

    def _mirror_floor(self, floor: Floor) -> None:
        width = floor.width
        for x0, y in floor.indices:
            x1 = width - 1 - x0
            if x0 < x1:
                floor.tiles[x0, y], floor.tiles[x1, y] = floor.tiles[x1, y], floor.tiles[x0, y]

    def _adjust_tokens(self, config: ConfigFile, board: Board, floor: Floor) -> None:
        for x, y in floor.indices:
            tile = floor.get_space(x, y)
            token_refs = list(tile.token_ids)  # Make a duplicate that we can modify.
            for token_ref in tile.token_ids:
                token_span = _get_token_span(config, board, token_ref)
                if token_span[0] > 1:
                    new_x = x - (token_span[0] - 1)
                    floor.get_space(new_x, y).append_token_id(token_ref)
                    token_refs.remove(token_ref)
            tile.token_ids = token_refs


def _get_token_span(config: ConfigFile, board: Board, token_ref: str) -> tuple[int, int]:
    token = board.tokens[token_ref]
    if not isinstance(token, ConcreteToken):
        return _DEFAULT_SPAN
    token_data = config.definitions.get_token(token.token_name)
    return token_data.span or _DEFAULT_SPAN
