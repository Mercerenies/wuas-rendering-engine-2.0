
from wuas.board import Board
from wuas.config import ConfigFile
from wuas.constants import SPACE_WIDTH, SPACE_HEIGHT
from wuas.output.abc import OutputProducer

from PIL import Image

from enum import IntEnum


class Layer(IntEnum):
    # The layer where we draw nothing. By definition, this layer has
    # nothing on it.
    VOID = -999
    # The layer of gaps, or empty white impassible space.
    GAP = 0
    # Any space which does not fall on another layer goes here.
    REGULAR = 1
    # The tokens on the board.
    TOKEN = 999


class Renderer:
    config: ConfigFile
    board: Board
    image: Image.Image

    def __init__(self, config: ConfigFile, board: Board) -> None:
        self.config = config
        self.board = board
        image_width = SPACE_WIDTH * board.width
        image_height = SPACE_HEIGHT * board.height
        self.image = Image.new("RGBA", (image_width, image_height))

    def render_layer(self, layer: Layer) -> None:
        self._render_spaces(layer)
        if layer is Layer.TOKEN:
            self._render_tokens()

    def _render_spaces(self, layer: Layer) -> None:
        for x, y in self.board.indices:
            space = self.board.get_space(x, y)
            if get_layer(space.space_name) is layer:
                space_data = self.config.definitions.get_space(space.space_name)
                space_image = self.config.spaces_png.select(space_data.coords)
                self.image.paste(space_image, (x * SPACE_WIDTH, y * SPACE_HEIGHT), space_image)

    def _render_tokens(self) -> None:
        for x, y in self.board.indices:
            space = self.board.get_space(x, y)
            topleft_x = x * SPACE_WIDTH
            topleft_y = y * SPACE_HEIGHT
            for token in space.get_tokens():
                token_data = self.config.definitions.get_token(token.token_name)
                token_image = self.config.tokens_png.select(token_data.thumbnail)  # TODO Span
                dx, dy = token.position
                self.image.paste(token_image, (topleft_x + dx, topleft_y + dy), token_image)

    def build(self) -> Image.Image:
        return self.image


def render_image(config: ConfigFile, board: Board) -> Image.Image:
    renderer = Renderer(config, board)
    for layer in Layer:
        renderer.render_layer(layer)
    return renderer.build()


def get_layer(space_name: str) -> Layer:
    """Which layer the spaces are drawn on. Gaps are always drawn
    before other spaces, so they sit on a layer below others.

    """
    if space_name == 'gap':
        return Layer.GAP
    else:
        return Layer.REGULAR


class DisplayedImageProducer(OutputProducer):

    def produce_output(self, config: ConfigFile, board: Board) -> None:
        image = render_image(config, board)
        image.show()


class SavedImageProducer(OutputProducer):
    output_filename: str

    def __init__(self, output_filename: str) -> None:
        self.output_filename = output_filename

    def produce_output(self, config: ConfigFile, board: Board) -> None:
        image = render_image(config, board)
        image.save(self.output_filename)
