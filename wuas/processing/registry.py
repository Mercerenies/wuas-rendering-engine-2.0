
"""Global registry of board processors. Any processor can register
itself with this registry using the @registered_processor decorator, and
processors can be queried by name from the REGISTERED_PROCESSORS
mapping."""

from __future__ import annotations

from wuas.processing.abc import BoardProcessor
from wuas.util.registry import ClassRegistry

REGISTERED_PROCESSORS = ClassRegistry[BoardProcessor]()

registered_processor = REGISTERED_PROCESSORS.register_class
