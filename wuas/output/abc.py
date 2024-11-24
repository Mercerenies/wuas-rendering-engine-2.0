
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from wuas.board import Board
from wuas.config import ConfigFile


class OutputProducer(ABC):
    """A class capable of producing output in some form from a
    configuration and a board object."""

    @abstractmethod
    def produce_output(self, config: ConfigFile, board: Board, args: OutputArgs) -> None:
        """Produces output in the format prescribed by this producer.
        This method should NOT modify the board.

        Note that this method returns None. The output produced should
        either be saved somewhere outside of Python (such as to a file)
        or otherwise stored on the producer object and made available
        via a builder-like API."""
        ...


@dataclass(frozen=True, kw_only=True)
class OutputArgs:
    output_filename: str | None = None
    floor_number: int | None = None

    UNEXPECTED_OUTPUT_FILENAME = "Unexpected argument --output-filename (-o) for output producer"
    UNEXPECTED_FLOOR_NUMBER = "Unexpected argument --floor-number (-F) for output producer"

    def assert_no_args(self) -> None:
        if self.output_filename is not None:
            raise ValueError(self.UNEXPECTED_OUTPUT_FILENAME)
        if self.floor_number is not None:
            raise ValueError(self.UNEXPECTED_FLOOR_NUMBER)
