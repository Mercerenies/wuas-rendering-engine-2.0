
"""The floors of the board are indexed by either finite integers or
the special sentinel infinity floor."""

from __future__ import annotations

from typing import Literal, ClassVar
from functools import total_ordering


@total_ordering
class FloorNumber:
    _value: int | Literal['inf']

    INFINITY: ClassVar[FloorNumber]

    def __init__(self, value: int | str) -> None:
        """Accepts an integer or a string. In case of a string, the
        string must either be the literal string 'inf', or a string
        representing a valid integer.

        Throws ValueError on invalid input.

        """
        if isinstance(value, str):
            value = value.strip()
            if value == 'inf':
                object.__setattr__(self, '_value', 'inf')
            else:
                try:
                    object.__setattr__(self, '_value', int(value))
                except ValueError:
                    raise ValueError(f"Invalid floor number {value!r}, expected an integer or 'inf'")
        else:
            object.__setattr__(self, '_value', value)

    @property
    def name(self) -> str:
        """The floor's name, as a string."""
        if isinstance(self._value, int):
            return str(self._value)
        else:
            return self._value

    def as_integer(self) -> int:
        """Throws ValueError on infinity."""
        if self._value == 'inf':
            raise ValueError("Cannot convert infinity floor to integer")
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FloorNumber):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(('FloorNumber', self._value))

    def __le__(self, other: FloorNumber) -> bool:
        if other._value == 'inf':
            return True
        elif self._value == 'inf':
            return False
        else:
            return self._value <= other._value

    def __add__(self, other: FloorNumber | int) -> FloorNumber:
        if isinstance(other, int):
            other = FloorNumber(other)
        if self._value == 'inf' or other._value == 'inf':
            return FloorNumber.INFINITY
        return FloorNumber(self._value + other._value)

    def __sub__(self, other: int) -> FloorNumber:
        if self._value == 'inf':
            return FloorNumber.INFINITY
        return FloorNumber(self._value - other)

    def is_infinite(self) -> bool:
        return self._value == 'inf'

    @classmethod
    def parse(cls, text: str) -> FloorNumber:
        """Parse a string as a floor number. Throws ValueError on
        failure. Alias for FloorNumber(text)."""
        return cls(text)

    def __str__(self) -> str:
        if self._value == 'inf':
            return '∞'
        return str(self._value)

    def __repr__(self) -> str:
        return f"FloorNumber({self!r})"


FloorNumber.INFINITY = FloorNumber('inf')
