
"""Argument parsing for WUAS movement sub-engine."""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass
class Arguments:
    original_args: argparse.Namespace
    input_filename: str
    config_filename: str
    validate: bool
    turn_log_file: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Movement rendering engine for WUAS',
    )
    parser.add_argument('-c', '--config-filename', required=True)
    parser.add_argument('-i', '--input-filename', required=True)
    parser.add_argument('--validate', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('turn_log_file')

    return parser.parse_args()


def interpret_args(namespace: argparse.Namespace) -> Arguments:
    return Arguments(
        original_args=namespace,
        input_filename=namespace.input_filename,
        config_filename=namespace.config_filename,
        validate=namespace.validate,
        turn_log_file=namespace.turn_log_file,
    )


def parse_and_interpret_args() -> Arguments:
    args = parse_args()
    return interpret_args(args)
