
"""Argument parsing for WUAS rendering engine."""

from __future__ import annotations

from wuas.output import OutputProducer
from wuas.output.registry import REGISTERED_PRODUCERS
from wuas.processing import BoardProcessor
from wuas.processing.registry import REGISTERED_PROCESSORS

from typing import Any
import argparse
from dataclasses import dataclass


@dataclass
class Arguments:
    original_args: argparse.Namespace
    input_filename: str
    config_filename: str
    validate: bool
    board_processors: list[BoardProcessor]
    output_producer: OutputProducer[Any]


class ArgumentsError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Rendering engine for WUAS',
    )
    parser.add_argument('-c', '--config-filename', required=True)
    parser.add_argument('-i', '--input-filename', required=True)
    parser.add_argument('--validate', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('instructions', nargs='*')

    _make_output_subparsers(parser)
    return parser.parse_args()


def _make_output_subparsers(parser: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers(required=True, dest='output_producer')
    for output_producer_name, output_producer_factory in REGISTERED_PRODUCERS.items():
        output_producer = output_producer_factory()
        subparser = subparsers.add_parser(output_producer_name)
        output_producer.init_subparser(subparser)


def interpret_args(namespace: argparse.Namespace) -> Arguments:
    config_filename = namespace.config_filename
    input_filename = namespace.input_filename

    board_processors = [interpret_processor(instruction) for instruction in namespace.instructions]
    output_producer = interpret_output_producer(namespace.output_producer)

    return Arguments(
        original_args=namespace,
        config_filename=config_filename,
        input_filename=input_filename,
        validate=namespace.validate,
        board_processors=board_processors,
        output_producer=output_producer,
    )


def interpret_output_producer(instruction: str) -> OutputProducer:
    try:
        return REGISTERED_PRODUCERS[instruction]()
    except KeyError:
        choices = ', '.join(sorted(REGISTERED_PRODUCERS.keys()))
        raise ArgumentsError(f"Invalid output producer {instruction}, choices are {choices}") from None


def interpret_processor(instruction: str) -> BoardProcessor:
    try:
        return REGISTERED_PROCESSORS[instruction]()
    except KeyError:
        choices = ', '.join(sorted(REGISTERED_PROCESSORS.keys()))
        raise ArgumentsError(f"Invalid board processor {instruction}, choices are {choices}") from None


def parse_and_interpret_args() -> Arguments:
    args = parse_args()
    return interpret_args(args)
