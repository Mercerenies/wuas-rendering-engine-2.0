
"""Parser for the configuration JSON file, as well as the other related
JSON files it references."""

from __future__ import annotations

from PIL import Image

import json
from typing import Any, Literal
from dataclasses import dataclass
from functools import cached_property


def normalize_space_name(name: str) -> str:
    """To make the datafile format more readable, a space whose name is
    '' is treated as a 'gap' space. This function performs that
    transformation, returning 'gap' if the input is '', or returning the
    input unmodified otherwise."""
    if name == '':
        return 'gap'
    else:
        return name


class ConfigFile:
    """A configuration file containing data about the spaces, items,
    tokens, and other effects available in a particular game of WUAS."""

    _json_data: Any

    def __init__(self, json_data: Any) -> None:
        """Construct a configuration object from the given JSON-like
        value."""
        self._json_data = json_data

    @classmethod
    def from_json(cls, filename: str) -> ConfigFile:
        """Read the configuration data from the JSON file with the given
        name."""
        with open(filename, 'r') as json_file:
            return cls(json.load(json_file))

    @cached_property
    def definitions(self) -> DefinitionsFile:
        """The definitions file which provides descriptions of effects."""
        return DefinitionsFile.from_json(filename=self._json_data['files']['dict'])

    @cached_property
    def spaces_png(self) -> SpacesPng:
        """The image representing all of the spaces."""
        return SpacesPng(Image.open(self._json_data['files']['spaces']))

    @cached_property
    def tokens_png(self) -> TokensPng:
        """The image representing all of the tokens, both player and otherwise."""
        return TokensPng(Image.open(self._json_data['files']['tokens']))

    @property
    def meta(self) -> dict[str, Any]:
        """A dictionary of metadata, whose format is unspecified but
        which can be used to store arbitrary key-value data in the
        configuration file."""
        return self._json_data['meta']


class DefinitionsFile:
    """The file containing the descriptions of all spaces, tokens, and
    other effects in the game."""

    _json_data: Any

    def __init__(self, json_data: Any) -> None:
        """Construct DefinitionsFile from a JSON-like structure."""
        self._json_data = json_data

    @classmethod
    def from_json(cls, filename: str) -> DefinitionsFile:
        """Parse DefinitionsFile from the given JSON file."""
        with open(filename, 'r') as json_file:
            return cls(json.load(json_file))

    def has_space(self, key: str) -> bool:
        """Returns true if the space with the given name exists. This
        function performs space name normalization with normalize_space_name."""
        try:
            self.get_space(key)
            return True
        except KeyError:
            return False

    def has_item(self, key: str) -> bool:
        """Returns true if the item with the given name exists."""
        try:
            self.get_item(key)
            return True
        except KeyError:
            return False

    def has_attribute(self, key: str) -> bool:
        """Returns true if the attribute with the given name exists."""
        try:
            self.get_attribute(key)
            return True
        except KeyError:
            return False

    def has_token(self, key: str) -> bool:
        """Returns true if the token with the given name exists."""
        try:
            self.get_token(key)
            return True
        except KeyError:
            return False

    def get_space(self, key: str) -> SpaceDefinition:
        """Returns the space with the given name, after normalizing with
        normalize_space_name. Raises KeyError if it doesn't exist."""
        key = normalize_space_name(key)
        return SpaceDefinition.from_json_data(self._json_data['spaces'][key])

    def get_item(self, key: str) -> ItemDefinition:
        """Returns the item with the given name, raising KeyError if it doesn't
        exist."""
        return ItemDefinition.from_json_data(self._json_data['items'][key])

    def get_attribute(self, key: str) -> AttributeDefinition:
        """Returns the attribute with the given name, raising KeyError
        if it doesn't exist."""
        return AttributeDefinition.from_json_data(self._json_data['attributes'][key])

    def get_token(self, key: str) -> TokenDefinition:
        """Returns the token with the given name, raising KeyError if it doesn't
        exist."""
        return TokenDefinition.from_json_data(self._json_data['tokens'][key])


@dataclass(frozen=True)
class SpaceDefinition:
    """The definition of a space, according to a DefinitionsFile."""

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
    """The definition of an item, according to a DefinitionsFile."""

    name: str
    desc: str

    @classmethod
    def from_json_data(cls, json_data: Any) -> ItemDefinition:
        return cls(
            name=json_data['name'],
            desc=json_data['desc'],
        )


@dataclass(frozen=True)
class AttributeDefinition:
    """The definition of a space attribute, according to a
    DefinitionsFile."""

    name: str
    outlinecolor: str | None
    outlineside: Literal['all', 'bottom']
    desc: str

    @classmethod
    def from_json_data(cls, json_data: Any) -> AttributeDefinition:
        return cls(
            name=json_data['name'],
            outlinecolor=json_data['outlinecolor'],
            outlineside=json_data.get('outlineside', 'all'),
            desc=json_data['desc'],
        )


@dataclass(frozen=True)
class TokenDefinition:
    """The definition of a token, according to a DefinitionsFile."""

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

    def is_player(self) -> bool:
        return self.stats == 'Player'


class SpacesPng:
    image: Image.Image

    def __init__(self, image: Image.Image) -> None:
        self.image = image

    def select(self, coords: tuple[int, int, int, int]) -> Image.Image:
        return self.image.crop(coords)


class TokensPng:
    image: Image.Image

    def __init__(self, image: Image.Image) -> None:
        self.image = image

    def select(self, coords: tuple[int, int], span: tuple[int, int] = (1, 1)) -> Image.Image:
        x_span, y_span = span
        x0, y0 = coords
        x1, y1 = x0 + TOKEN_WIDTH * x_span, y0 + TOKEN_HEIGHT * y_span
        return self.image.crop((x0, y0, x1, y1))


TOKEN_WIDTH = 16
TOKEN_HEIGHT = 16
