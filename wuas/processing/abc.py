
from abc import ABC, abstractmethod

from wuas.board import Board
from wuas.config import ConfigFile


class BoardProcessor(ABC):

    @abstractmethod
    def run(self, config: ConfigFile, board: Board) -> None:
        ...
