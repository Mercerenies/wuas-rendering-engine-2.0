
"""Output file formats. This module exports OutputProducer and several
useful subclasses of it."""

from .abc import OutputProducer, OutputArgs
from wuas.util import import_immediate_submodules

__all__ = (
    'OutputProducer', 'OutputArgs',
)

# Load all modules in this directory, to allow processors to register
# themselves.
import_immediate_submodules(__file__, __name__)
