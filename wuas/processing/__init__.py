
"""Board processors which modify the board before a final OutputProducer
creates output."""

from .abc import BoardProcessor

import os
import os.path
import importlib

__all__ = (
    'BoardProcessor',
)

# Load all modules in this directory, to allow processors to register
# themselves.
current_module_name = __name__.removesuffix('.__init__')
for current_file in os.listdir(os.path.dirname(__file__)):
    if current_file.endswith('.py') and current_file != '__init__':
        module_name = current_module_name + "." + current_file[:-3]
        importlib.import_module(module_name)
    else:
        full_path = os.path.join(os.path.dirname(__file__), current_file)
        init_py = os.path.join(full_path, '__init__.py')
        if os.path.isdir(full_path) and os.path.isfile(init_py):
            module_name = current_module_name + "." + current_file
            importlib.import_module(module_name)
