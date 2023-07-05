
"""Output format which renders to a PNG image."""

from wuas.board import Board, Floor
from wuas.config import ConfigFile
from wuas.constants import SPACE_WIDTH, SPACE_HEIGHT
from wuas.output.abc import OutputProducer

from PIL import Image, ImageDraw

from enum import IntEnum


class Layer(IntEnum):
    """Drawing spaces is done via layers, to make sure everything looks
    reasonable in the resulting image. Every space type has a layer
    intrinsic to it, which can be queried via get_layer. Spaces with a
    lower layer will draw first, allowing those with a higher layer to
    draw on top of them. The defined layers, in ascending order, are

    * VOID - The minimum layer. By definition, nothing is on this layer,
      and it appears behind everything else.
    * GAP - The layer of gaps, i.e. empty white impassible spaces.
    * REGULAR - The layer of all spaces that do not have special
      drawing rules.
    * TOKEN - No spaces draw on this layer. This is the layer of
      token objects, such as players and items, which draw on top
      of the space layer."""

    VOID = -999
    GAP = 0
    REGULAR = 1
    TOKEN = 999


class Renderer:
    """Image renderer for converting a board object into a PNG image
    file. For most simpleuse cases, you can simply use one of the
    OutputProducers defined in this module and won't need to interface
    directly with this class. But this class can be used for
    fine-grained control over layering."""

    config: ConfigFile
    floor: Floor
    image: Image.Image

    def __init__(self, config: ConfigFile, floor: Floor) -> None:
        self.config = config
        self.floor = floor
        image_width = SPACE_WIDTH * floor.width
        image_height = SPACE_HEIGHT * floor.height
        self.image = Image.new("RGBA", (image_width, image_height))

    def render_layer(self, layer: Layer) -> None:
        """Render the spaces associated with the given layer. If the
        layer is Layer.TOKEN, also render the tokens on the board."""
        self._render_spaces(layer)
        if layer is Layer.TOKEN:
            self._render_tokens()

    def _render_spaces(self, layer: Layer) -> None:
        for x, y in self.floor.indices:
            space = self.floor.get_space(x, y)
            if get_layer(space.space_name) is layer:
                space_data = self.config.definitions.get_space(space.space_name)
                space_image = self.config.spaces_png.select(space_data.coords)
                self.image.paste(space_image, (x * SPACE_WIDTH, y * SPACE_HEIGHT), space_image)
                # Attributes for this space
                for attribute in space.get_attributes():
                    attribute_data = self.config.definitions.get_attribute(attribute.name)
                    if attribute_data.outlinecolor is not None:
                        self._highlight_space(x, y, attribute_data.outlinecolor)

    def _render_tokens(self) -> None:
        for x, y in self.floor.indices:
            space = self.floor.get_space(x, y)
            topleft_x = x * SPACE_WIDTH
            topleft_y = y * SPACE_HEIGHT
            for token in space.get_tokens():
                token_data = self.config.definitions.get_token(token.token_name)
                token_image = self.config.tokens_png.select(token_data.thumbnail)  # TODO Span
                dx, dy = token.position
                self.image.paste(token_image, (topleft_x + dx, topleft_y + dy), token_image)

    def _highlight_space(self, x: int, y: int, outline_color: str) -> None:
        draw = ImageDraw.Draw(self.image)
        x0 = x * SPACE_WIDTH + 2
        y0 = y * SPACE_HEIGHT + 2
        x1 = x0 + SPACE_WIDTH - 4
        y1 = y0 + SPACE_HEIGHT - 4
        draw.line(
            [(x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)],
            fill=outline_color,
            width=3,
        )

    def build(self) -> Image.Image:
        """Return the image being constructed. This renderer should be
        considered consumed once this method has been called."""
        return self.image


def render_image(config: ConfigFile, floor: Floor) -> Image.Image:
    """Render the floor to an image file by drawing the layers in
    order."""
    renderer = Renderer(config, floor)
    for layer in Layer:
        renderer.render_layer(layer)
    return renderer.build()


def get_layer(space_name: str) -> Layer:
    """Which layer the spaces are drawn on. Gaps are always drawn
    before other spaces, so they sit on a layer below others."""
    if space_name == 'gap':
        return Layer.GAP
    else:
        return Layer.REGULAR


class DisplayedImageProducer(OutputProducer):
    """OutputProducer that outputs an image to a new on-screen window."""
    _floor_number: int

    def __init__(self, floor_number: int) -> None:
        self._floor_number = floor_number

    def produce_output(self, config: ConfigFile, board: Board) -> None:
        image = render_image(config, board.floors[self._floor_number])
        image.show()


class SavedImageProducer(OutputProducer):
    """OutputProducer that outputs an image to the given file."""
    output_filename: str
    _floor_number: int

    def __init__(self, output_filename: str, floor_number: int) -> None:
        self.output_filename = output_filename
        self._floor_number = floor_number

    def produce_output(self, config: ConfigFile, board: Board) -> None:
        image = render_image(config, board.floors[self._floor_number])
        image.save(self.output_filename)
