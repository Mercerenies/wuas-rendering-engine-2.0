
"""Very rudimentary implementation of a bidirectional graph (really
just a GraphEdge dataclass right now), for the purposes of
implementing the "Party!" highway."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GraphEdge:
    from_node: str
    to_node: str

    @classmethod
    def parse_from_line(cls, line: str) -> GraphEdge:
        from_node, to_node = line.split('--')
        return cls(from_node, to_node)

    def to_data_str(self) -> str:
        return self.from_node + '--' + self.to_node
