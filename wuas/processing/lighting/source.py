
from __future__ import annotations

from abc import ABC, abstractmethod


class LightSourceSupplier(ABC):

    @abstractmethod
    def get_light_source(self, position: tuple[int, int]) -> int:
        ...
