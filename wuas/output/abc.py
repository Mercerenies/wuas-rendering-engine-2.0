
from abc import ABC, abstractmethod

from wuas.board import Board
from wuas.config import ConfigFile


class OutputProducer(ABC):

    @abstractmethod
    def produce_output(self, config: ConfigFile, board: Board) -> None:
        ...
