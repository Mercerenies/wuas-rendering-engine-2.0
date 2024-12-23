
"""Global registry of board output producers. Any OutputProducer can
register itself with this registry using the @registered_processor
decorator, and processors can be queried by name from the
REGISTERED_PROCESSORS mapping.

"""

from __future__ import annotations

from typing import Any

from wuas.output.abc import OutputProducer
from wuas.util.registry import ClassRegistry

REGISTERED_PRODUCERS = ClassRegistry[OutputProducer[Any]]()

registered_producer = REGISTERED_PRODUCERS.register_class
