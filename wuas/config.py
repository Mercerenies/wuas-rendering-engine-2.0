
from __future__ import annotations

import json
from typing import Any
from dataclasses import dataclass

class ConfigFile:
    _json_data: Any

    def __init__(self, json_data: Any) -> None:
        self._json_data = json_data

    @classmethod
    def from_json(cls, filename: str) -> ConfigFile:
        with open(filename, 'r') as json_file:
            return cls(json.load(json_file))

    def get_definitions(self) -> DefinitionsFile:
        return DefinitionsFile.from_json(filename=self._json_data['files']['dict'])


class DefinitionsFile:
    _json_data: Any

    def __init__(self, json_data: Any) -> None:
        self._json_data = json_data

    @classmethod
    def from_json(cls, filename: str) -> DefinitionsFile:
        with open(filename, 'r') as json_file:
            return cls(json.load(json_file))

    def has_space(self, key: str) -> bool:
        try:
            self.get_space(key)
            return True
        except KeyError:
            return False

    def has_item(self, key: str) -> bool:
        try:
            self.get_item(key)
            return True
        except KeyError:
            return False

    def has_token(self, key: str) -> bool:
        try:
            self.get_token(key)
            return True
        except KeyError:
            return False

    def get_space(self, key: str) -> SpaceDefinition:
        # As a hard-coded alias, spaces that are totally empty are
        # treated as "gap" spaces.
        if key == '':
            key = 'gap'
        return SpaceDefinition.from_json_data(self._json_data['spaces'][key])

    def get_item(self, key: str) -> ItemDefinition:
        return ItemDefinition.from_json_data(self._json_data['items'][key])

    def get_token(self, key: str) -> TokenDefinition:
        return TokenDefinition.from_json_data(self._json_data['tokens'][key])


@dataclass(frozen=True)
class SpaceDefinition:
    name: str
    coords: tuple[int, int, int, int]
    visual: str
    desc: str

    @classmethod
    def from_json_data(cls, json_data: Any) -> SpaceDefinition:
        x1, y1, x2, y2 = [int(coord) for coord in json_data['coords'].split(',')]
        return cls(
            name=json_data['name'],
            coords=(x1, y1, x2, y2),
            visual=json_data['visual'],
            desc=json_data['desc'],
        )


@dataclass(frozen=True)
class ItemDefinition:
    name: str
    desc: str

    @classmethod
    def from_json_data(cls, json_data: Any) -> ItemDefinition:
        return cls(
            name=json_data['name'],
            desc=json_data['desc'],
        )


@dataclass(frozen=True)
class TokenDefinition:
    name: str
    stats: str
    thumbnail: tuple[int, int]
    desc: str

    @classmethod
    def from_json_data(cls, json_data: Any) -> TokenDefinition:
        x, y = [int(coord) for coord in json_data['thumbnail']]
        return cls(
            name=json_data['name'],
            stats=json_data['stats'],
            thumbnail=(x, y),
            desc=json_data['desc'],
        )
