
"""Board processors which modify the board before a final OutputProducer
creates output."""

from .abc import BoardProcessor
from .lighting import LightingProcessor

import os
import os.path
import importlib

__all__ = (
    'BoardProcessor', 'LightingProcessor',
)

# Load all modules in this directory, to allow processors to register
# themselves. (TODO This excludes directories)
_files = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.py') and f != '__init__.py']
for current_file in _files:
    importlib.import_module(__name__ + "." + current_file[:-3])
