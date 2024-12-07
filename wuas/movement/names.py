
from __future__ import annotations

from abc import ABC, abstractmethod

from wuas.config import ConfigFile, DefinitionsFile


class PlayerNamer(ABC):
    """Abstract base class for anything capable of translating player
    IDs into player names."""

    @abstractmethod
    def get_name(self, player_id: str) -> str:
        """Returns the player's name, or raises ValueError if the ID
        is invalid."""
        ...


class ConfigPlayerNamer(PlayerNamer):
    """PlayerNamer based on a DefinitionsFile."""
    _definitions: DefinitionsFile

    def __init__(self, defs: DefinitionsFile | ConfigFile, /) -> None:
        if isinstance(defs, ConfigFile):
            defs = defs.definitions
        self._definitions = defs

    def get_name(self, player_id: str) -> str:
        try:
            token = self._definitions.get_token(player_id)
        except KeyError:
            raise ValueError(f"Invalid player ID: {player_id!r}")
        return token.name
