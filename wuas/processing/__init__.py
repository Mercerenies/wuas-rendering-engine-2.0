
"""Board processors which modify the board before a final OutputProducer
creates output."""

from .abc import BoardProcessor
from .lighting import LightingProcessor

__all__ = (
    'BoardProcessor', 'LightingProcessor',
)
