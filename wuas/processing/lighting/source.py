
from __future__ import annotations

from wuas.floornumber import FloorNumber

from abc import ABC, abstractmethod


class LightSourceSupplier(ABC):
    """A class capable of getting the level of light being emitted from
    a given location."""

    @abstractmethod
    def get_light_source(self, position: tuple[int, int, FloorNumber]) -> int:
        """Returns the positive light level being emitted from this
        location, or zero if the location does not emit light. Should
        return IndexError if out of bounds."""
        ...
