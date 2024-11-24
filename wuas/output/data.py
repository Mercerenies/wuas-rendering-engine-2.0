
"""Output format that's equivalent to the input format. The resulting
file will be semantically equivalent to the original, but it may not
be exactly equal.

For instance, this file will normalize whitespace. It will also always
output the most recent file format version, even if the input file was
given in an earlier format."""

from __future__ import annotations

from wuas.board import Board, Floor, Token, ConcreteToken, HiddenToken
from wuas.config import ConfigFile
from wuas.loader import SPACE_LABEL_MARKER
from wuas.output.abc import OutputProducer
from wuas.output.registry import REGISTERED_PRODUCERS

import sys
import argparse
from typing import TextIO

# For Emacs compatibility
COMMENT_LINES = (
    '# -*- mode: Text; truncate-lines: t -*-',
)

SPACE_TEXT_WIDTH = 10
HEADER_SLOT = '+' + '-' * SPACE_TEXT_WIDTH
CURRENT_VERSION_NUMBER = 5


def render_to_data_file(board: Board, output_file: TextIO) -> None:
    """Render the board to the given file-like object, which must be
    opened for output."""

    # Introductory comments
    for comment_line in COMMENT_LINES:
        output_file.write(comment_line + '\n')
    output_file.write('\n')

    # Versioning
    output_file.write(str(CURRENT_VERSION_NUMBER) + '\n')

    # Meta data
    for k, v in board.meta.items():
        output_file.write(f"{k}: {v}\n")
    output_file.write('\n')

    # Board contents
    for z, floor in board.floors.items():
        output_file.write(f"floor={z}\n")
        _print_board_contents(floor, output_file)
    output_file.write("\n")

    # Token reference
    _print_token_references(board, output_file)
    output_file.write('\n')

    # Attribute reference
    _print_attribute_references(board, output_file)
    output_file.write('\n')

    # Graph data
    _print_graph_data(board, output_file)
    output_file.write('\n')


def _print_board_contents(floor: Floor, output_file: TextIO) -> None:
    width = floor.width
    height = floor.height
    separator_row = HEADER_SLOT * width + '+'

    for y in range(height):
        output_file.write(separator_row + '\n')
        # Spaces layer
        output_file.write('|')
        for x in range(width):
            space = floor.get_space(x, y)
            space_text = space.space_name + ''.join(space.attribute_ids)
            output_file.write(' {:<{}}|'.format(space_text, SPACE_TEXT_WIDTH - 1))
        output_file.write('\n')
        # Tokens layer
        output_file.write('|')
        for x in range(width):
            space = floor.get_space(x, y)
            token_layer_text = ''.join(space.token_ids)
            if space.space_label is not None:
                token_layer_text += SPACE_LABEL_MARKER + space.space_label
            output_file.write(' {:<{}}|'.format(token_layer_text, SPACE_TEXT_WIDTH - 1))
        output_file.write('\n')
    output_file.write(separator_row + '\n\n')


def _print_token_references(board: Board, output_file: TextIO) -> None:
    max_token_length = max(len(_concretify_token(token).token_name) for token in board.tokens.values())
    max_item_length = max(len(_concretify_token(token).item_name or 'nil') for token in board.tokens.values())
    for key, value in board.tokens.items():
        token = _concretify_token(value)
        output_file.write("{} {:<{}} {:<{}} {:>2} {:>2}\n".format(
            key,
            token.token_name,
            max_token_length,
            token.item_name or "nil",
            max_item_length,
            token.position[0],
            token.position[1],
        ))


def _concretify_token(token: Token) -> ConcreteToken:
    if isinstance(token, HiddenToken):
        return token.to_concrete()
    else:
        return token


def _print_attribute_references(board: Board, output_file: TextIO) -> None:
    for key, value in board.attributes.items():
        output_file.write(f"{key} {value.name}\n")


def _print_graph_data(board: Board, output_file: TextIO) -> None:
    for edge in board.graph_edges:
        output_file.write(edge.to_data_str() + "\n")


class DatafileProducer(OutputProducer):
    """OutputProducer that outputs to a given file-like object."""

    _io: TextIO

    def __init__(self, io: TextIO) -> None:
        """A datafile producer for the given file-like object. The
        object must be opened for writing. This class is NOT responsible
        for closing the file object."""
        self._io = io

    @classmethod
    def stdout(cls) -> DatafileProducer:
        """A datafile producer which prints to sys.stdout."""
        return cls(sys.stdout)

    def produce_output(self, config: ConfigFile, board: Board, args: argparse.Namespace) -> None:
        render_to_data_file(board, self._io)

    def init_subparser(self, subparser: argparse.ArgumentParser) -> None:
        """DatafileProducer accepts no subarguments."""
        pass


REGISTERED_PRODUCERS.register_callable('datafile', DatafileProducer.stdout)
