
from __future__ import annotations

from abc import ABC, abstractmethod

from wuas.config import ConfigFile, DefinitionsFile


class ObjectNamer(ABC):
    """Abstract base class for anything capable of translating player
    IDs into player names and space IDs into space names."""

    @abstractmethod
    def get_player_name(self, player_id: str) -> str:
        """Returns the player's name, or raises ValueError if the ID
        is invalid."""
        ...

    @abstractmethod
    def get_space_name(self, space_id: str) -> str:
        """Returns the space's name, or raises ValueError if the ID
        is invalid."""
        ...


class ConfigObjectNamer(ObjectNamer):
    """PlayerNamer based on a DefinitionsFile."""
    _definitions: DefinitionsFile

    def __init__(self, defs: DefinitionsFile | ConfigFile, /) -> None:
        if isinstance(defs, ConfigFile):
            defs = defs.definitions
        self._definitions = defs

    def get_player_name(self, player_id: str) -> str:
        try:
            token = self._definitions.get_token(player_id)
        except KeyError:
            raise ValueError(f"Invalid player ID: {player_id!r}")
        return token.name

    def get_space_name(self, space_id: str) -> str:
        try:
            space = self._definitions.get_effect_space(space_id)
        except KeyError:
            raise ValueError(f"Invalid space ID: {space_id!r}")
        return space.name
