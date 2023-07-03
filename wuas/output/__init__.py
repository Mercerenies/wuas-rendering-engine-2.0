
"""Output file formats. This module exports OutputProducer and several
useful subclasses of it."""

from .abc import OutputProducer
from .image import DisplayedImageProducer, SavedImageProducer
from .json import JsonProducer
from .data import DatafileProducer

__all__ = (
    'OutputProducer',
    'DisplayedImageProducer', 'SavedImageProducer',
    'JsonProducer',
    'DatafileProducer',
)

# TODO Registry-like API, similar to what we have for processors.
