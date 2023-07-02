
"""Output format that's equivalent to the input format. The resulting
file will be semantically equivalent to the original, but it may not
be exactly equal.

For instance, this file will normalize whitespace. It will also always
output the most recent file format version, even if the input file was
given in an earlier format.

"""

from __future__ import annotations

from wuas.board import Board

from typing import TextIO

# For Emacs compatibility
COMMENT_LINES = (
    '# -*- mode: Text; truncate-lines: t -*-',
)

SPACE_TEXT_WIDTH = 10
HEADER_SLOT = '+' + '-' * SPACE_TEXT_WIDTH


def render_to_data_file(board: Board, output_file: TextIO) -> None:

    # Introductory comments
    for comment_line in COMMENT_LINES:
        output_file.write(comment_line + '\n')
    output_file.write('\n')

    # Versioning
    output_file.write('2\n')

    # Meta data
    for k, v in board.meta.items():
        output_file.write(f"{k}: {v}\n")
    output_file.write('\n')

    # Board contents
    _print_board_contents(board, output_file)

    # Token reference
    _print_token_references(board, output_file)


def _print_board_contents(board: Board, output_file: TextIO) -> None:
    width = board.width
    height = board.height
    separator_row = HEADER_SLOT * width + '+'

    for y in range(height):
        output_file.write(separator_row + '\n')
        # Spaces layer
        output_file.write('|')
        for x in range(width):
            space = board.get_space(x, y)
            output_file.write(' {:<{}}|'.format(space.space_name, SPACE_TEXT_WIDTH - 1))
        output_file.write('\n')
        # Tokens layer
        output_file.write('|')
        for x in range(width):
            space = board.get_space(x, y)
            output_file.write(' {:<{}}|'.format(''.join(space.token_ids), SPACE_TEXT_WIDTH - 1))
        output_file.write('\n')
    output_file.write(separator_row + '\n\n')


def _print_token_references(board: Board, output_file: TextIO) -> None:
    max_token_length = max(len(token.token_name) for token in board.tokens.values())
    max_item_length = max(len(token.item_name or 'nil') for token in board.tokens.values())
    for key, value in board.tokens.items():
        output_file.write("{} {:<{}} {:<{}} {:>2} {:>2}\n".format(
            key,
            value.token_name,
            max_token_length,
            value.item_name or "nil",
            max_item_length,
            value.position[0],
            value.position[1],
        ))
