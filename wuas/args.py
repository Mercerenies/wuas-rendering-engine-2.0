
"""Argument parsing for WUAS rendering engine."""

from __future__ import annotations

from wuas.output import OutputProducer, DisplayedImageProducer, SavedImageProducer, JsonProducer, DatafileProducer
from wuas.processing import BoardProcessor
from wuas.processing.registry import REGISTERED_PROCESSORS

import argparse
from dataclasses import dataclass


@dataclass
class Arguments:
    input_filename: str
    output_filename: str | None
    config_filename: str
    validate: bool
    board_processors: list[BoardProcessor]
    output_producer: OutputProducer


class ArgumentsError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Rendering engine for WUAS',
    )
    parser.add_argument('-c', '--config-filename', required=True)
    parser.add_argument('-i', '--input-filename', required=True)
    parser.add_argument('-o', '--output-filename')
    parser.add_argument('--validate', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('instructions', nargs='+')
    return parser.parse_args()


def interpret_args(namespace: argparse.Namespace) -> Arguments:
    config_filename = namespace.config_filename
    input_filename = namespace.input_filename
    output_filename = namespace.output_filename

    board_processors = [interpret_processor(instruction) for instruction in namespace.instructions[:-1]]
    output_producer = interpret_output_producer(namespace.instructions[-1], output_filename)

    return Arguments(
        config_filename=config_filename,
        input_filename=input_filename,
        output_filename=output_filename,
        validate=namespace.validate,
        board_processors=board_processors,
        output_producer=output_producer,
    )


def interpret_output_producer(instruction: str, output_filename: str | None) -> OutputProducer:
    choices = 'show-image, save-image, json, datafile'
    match instruction:
        case "show-image":
            if output_filename is not None:
                raise ArgumentsError("show-image does not take an output file argument")
            return DisplayedImageProducer()
        case "save-image":
            if output_filename is None:
                raise ArgumentsError("save-image requires an output file argument")
            return SavedImageProducer(output_filename)
        case "json":
            if output_filename is not None:
                raise ArgumentsError("json does not take an output file argument")
            return JsonProducer.stdout()
        case "datafile":
            if output_filename is not None:
                raise ArgumentsError("datafile does not take an output file argument")
            return DatafileProducer.stdout()
        case _:
            raise ArgumentsError(f"Invalid output producer {instruction}, choices are {choices}")


def interpret_processor(instruction: str) -> BoardProcessor:
    choices = ', '.join(sorted(REGISTERED_PROCESSORS.keys()))
    try:
        return REGISTERED_PROCESSORS[instruction]()
    except KeyError:
        choices = ', '.join(sorted(REGISTERED_PROCESSORS.keys()))
        raise ArgumentsError(f"Invalid board processor {instruction}, choices are {choices}") from None


def parse_and_interpret_args() -> Arguments:
    args = parse_args()
    return interpret_args(args)
