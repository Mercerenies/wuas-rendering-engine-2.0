
"""Validator for a WUAS board."""

from __future__ import annotations

from wuas.board import Board, BoardIntegrityError, HiddenToken
from wuas.config import ConfigFile


class ValidationError(Exception):
    pass


def validate(config: ConfigFile, board: Board) -> None:
    """Perform sanity checks on the board, making sure that all
    references spaces, tokens, and items actually exist in the
    configuration file. On validation failure, a ValidationError is
    raised. On success, this function returns None."""
    definitions = config.definitions
    unique_space_labels = set()
    for x, y, z in board.indices:
        try:
            space = board.get_space(x, y, z)
            tokens = space.get_tokens()
            attrs = space.get_attributes()
        except BoardIntegrityError as exc:
            raise ValidationError("Integrity error in the board .dat file") from exc
        # Verify that the space and any tokens/items on it actually
        # exist.
        if not definitions.has_any_space(space.space_name):
            raise ValidationError(f"No such space {space.space_name}")
        for token_data in tokens:
            if isinstance(token_data, HiddenToken):
                continue  # Nothing to validate for hidden tokens.
            if not definitions.has_token(token_data.token_name):
                raise ValidationError(f"No such token {token_data.token_name}")
            if token_data.item_name and not definitions.has_item(token_data.item_name):
                raise ValidationError(f"No such item {token_data.item_name}")
        for attr_data in attrs:
            if not definitions.has_attribute(attr_data.name):
                raise ValidationError(f"No such attribute {attr_data.name}")
        # Verify that the space label, if present, is unique.
        if space.space_label is not None:
            if space.space_label in unique_space_labels:
                raise ValidationError(f"Duplicate space label {space.space_label}")
            unique_space_labels.add(space.space_label)
    # Verify that any graph edges represent spaces that exist.
    for graph_edge in board.graph_edges:
        if graph_edge.from_node not in unique_space_labels:
            raise ValidationError(f"No such space label {graph_edge.from_node}")
        if graph_edge.to_node not in unique_space_labels:
            raise ValidationError(f"No such space label {graph_edge.to_node}")
