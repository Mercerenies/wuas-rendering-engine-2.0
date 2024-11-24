
"""Board processors which modify the board before a final OutputProducer
creates output."""

from .abc import BoardProcessor
from wuas.util import import_immediate_submodules

import os
import os.path
import importlib

__all__ = (
    'BoardProcessor',
)

# Load all modules in this directory, to allow processors to register
# themselves.
import_immediate_submodules(__file__, __name__)
