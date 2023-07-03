
from __future__ import annotations

from wuas.processing.lighting.source import LightSourceSupplier
from wuas.board import Board, Token

from dataclasses import dataclass
from typing import Any


@dataclass
class LightingConfig:
    """The portion of the configuration metadata which represents the
    lighting engine's settings."""
    darkness: str
    spaces: dict[str, int]
    items: dict[str, int]
    tokens: dict[str, int]
    adjacency: dict[str, str]
    diminishing: dict[str, int]

    @classmethod
    def from_json(cls, json_data: Any) -> LightingConfig:
        return LightingConfig(
            darkness=json_data['darkness'],
            spaces=_validate_dict(json_data['spaces']),
            items=_validate_dict(json_data['items']),
            tokens=_validate_dict(json_data['tokens']),
            adjacency=json_data['adjacency'],
            diminishing=json_data['diminishing'],
        )


def _validate_dict(input_dict: Any) -> dict[Any, Any]:
    assert isinstance(input_dict, dict)
    for key in input_dict:
        assert isinstance(input_dict[key], int)
    return input_dict


DEFAULT_SPACE_LIGHT = 0
DEFAULT_TOKEN_LIGHT = 3
DEFAULT_ITEM_LIGHT = 1


class ConfigLightSourceSupplier(LightSourceSupplier):
    """Light source supplier that reads from the board and the given
    lighting configuration file."""
    _config: LightingConfig
    _board: Board

    def __init__(self, config: LightingConfig, board: Board) -> None:
        self._config = config
        self._board = board

    def get_light_source(self, position: tuple[int, int]) -> int:
        x, y = position
        space = self._board.get_space(x, y)
        lights = [self._token_light(token) for token in space.get_tokens()]
        lights.append(self._config.spaces.get(space.space_name, DEFAULT_SPACE_LIGHT))
        return max(lights)

    def _token_light(self, token: Token) -> int:
        if token.item_name is not None:
            return self._config.items.get(token.item_name, DEFAULT_ITEM_LIGHT)
        else:
            return self._config.tokens.get(token.token_name, DEFAULT_TOKEN_LIGHT)
