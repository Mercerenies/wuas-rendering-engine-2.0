
from __future__ import annotations

from abc import ABC, abstractmethod

from wuas.board import Board
from wuas.config import ConfigFile

import argparse


class OutputProducer(ABC):
    """A class capable of producing output in some form from a
    configuration and a board object."""

    # TODO: Stronger typing on args?
    @abstractmethod
    def produce_output(self, config: ConfigFile, board: Board, args: argparse.Namespace) -> None:
        """Produces output in the format prescribed by this producer.
        This method should NOT modify the board.

        Note that this method returns None. The output produced should
        either be saved somewhere outside of Python (such as to a file)
        or otherwise stored on the producer object and made available
        via a builder-like API."""
        ...

    @abstractmethod
    def init_subparser(self, subparser: argparse.ArgumentParser) -> None:
        """Initializes the subparser which will be used to parse
        arguments for this particular output producer."""
        ...
