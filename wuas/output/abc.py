
from abc import ABC, abstractmethod

from wuas.board import Board
from wuas.config import ConfigFile


class OutputProducer(ABC):
    """A class capable of producing output in some form from a
    configuration and a board object."""

    @abstractmethod
    def produce_output(self, config: ConfigFile, board: Board) -> None:
        """Produces output in the format prescribed by this producer.
        This method should NOT modify the board.

        Note that this method returns None. The output produced should
        either be saved somewhere outside of Python (such as to a file)
        or otherwise stored on the producer object and made available
        via a builder-like API."""
        ...
