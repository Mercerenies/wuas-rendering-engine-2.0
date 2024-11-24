
from __future__ import annotations

from abc import ABC, abstractmethod
import argparse
from dataclasses import dataclass

from wuas.board import Board
from wuas.config import ConfigFile
from wuas.util import to_dataclass_checked


class OutputProducer[A](ABC):
    """A class capable of producing output in some form from a
    configuration and a board object.

    The generic type A shall be the type containing the additional
    arguments (those produced by the subparser from init_subparser).
    This MUST be a dataclass type and will be used to strongly
    typecheck the types of the arguments from the subparser.

    """

    ARGUMENTS_TYPE: type[A]

    @abstractmethod
    def produce_output(self, config: ConfigFile, board: Board, args: A) -> None:
        """Produces output in the format prescribed by this producer.
        This method should NOT modify the board.

        Note that this method returns None. The output produced should
        either be saved somewhere outside of Python (such as to a file)
        or otherwise stored on the producer object and made available
        via a builder-like API."""
        ...

    def produce_output_checked(self, config: ConfigFile, board: Board, args: argparse.Namespace) -> None:
        checked_args = to_dataclass_checked(self.ARGUMENTS_TYPE, args)
        return self.produce_output(config, board, checked_args)

    @abstractmethod
    def init_subparser(self, subparser: argparse.ArgumentParser) -> None:
        """Initializes the subparser which will be used to parse
        arguments for this particular output producer."""
        ...


@dataclass(frozen=True)
class NoArguments:
    """Empty dataclass, for output producers which do not use any
    additional arguments."""
    pass
