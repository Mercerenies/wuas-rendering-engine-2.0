
from abc import ABC, abstractmethod

from wuas.board import Board
from wuas.config import ConfigFile


class BoardProcessor(ABC):
    """A BoardProcessor modifies the board in-place."""

    @abstractmethod
    def run(self, config: ConfigFile, board: Board) -> None:
        ...
