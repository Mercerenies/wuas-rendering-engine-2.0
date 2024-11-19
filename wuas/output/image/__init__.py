
"""Output format which renders to a PNG image."""

from __future__ import annotations

from wuas.util import draw_dotted_line
from wuas.board import Board, Floor, Space
from wuas.constants import SPACE_WIDTH, SPACE_HEIGHT, Layer
from wuas.config import ConfigFile, find_matching_for_layer
from wuas.output.abc import OutputProducer
from .majora import MAJORAS_MOON_LAYER, render_moon

from PIL import Image, ImageDraw

from typing import Set, Iterable, NamedTuple, Literal


class AttributeColor(NamedTuple):
    color: str
    side: Literal['all', 'bottom']


class Renderer:
    """Image renderer for converting a board object into a PNG image
    file. For most simpleuse cases, you can simply use one of the
    OutputProducers defined in this module and won't need to interface
    directly with this class. But this class can be used for
    fine-grained control over layering."""

    config: ConfigFile
    board: Board
    floor_number: int
    floor: Floor
    image: Image.Image

    def __init__(self, config: ConfigFile, board: Board, floor_number: int, floor: Floor) -> None:
        self.config = config
        self.floor_number = floor_number
        self.floor = floor
        self.board = board
        image_width = SPACE_WIDTH * floor.width
        image_height = SPACE_HEIGHT * floor.height
        self.image = Image.new("RGBA", (image_width, image_height))

    def render_layer(self, layer: Layer) -> None:
        """Render the spaces associated with the given layer. If the
        layer is Layer.TOKEN, also render the tokens on the board."""
        self._render_spaces(layer)
        if layer is Layer.HIGHWAY:
            self._render_highway()
        if layer is MAJORAS_MOON_LAYER:
            render_moon(self)
        if layer is Layer.TOKEN:
            self._render_tokens()

    def get_attribute_colors(self, space: Space) -> Set[AttributeColor]:
        result = set()
        for attribute in space.get_attributes():
            attribute_data = self.config.definitions.get_attribute(attribute.name)
            if attribute_data.outlinecolor is not None:
                result.add(AttributeColor(color=attribute_data.outlinecolor, side=attribute_data.outlineside))
        return result

    def _render_spaces(self, layer: Layer) -> None:
        for x, y in self.floor.indices:
            space = self.floor.get_space(x, y)
            space_data = find_matching_for_layer(
                config=self.config,
                space=self.config.definitions.get_any_space_as_composite(space.space_name),
                layer=layer,
            )
            if space_data:
                space_image = self.config.spaces_png.select(space_data.coords)
                self.image.paste(space_image, (x * SPACE_WIDTH, y * SPACE_HEIGHT), space_image)
                # Attributes for this space
                self._highlight_space(x, y, self.get_attribute_colors(space))

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

    def _render_highway(self) -> None:
        draw = ImageDraw.Draw(self.image)
        for edge in self.board.graph_edges:
            src_x, src_y, src_z = self.board.labels_map[edge.from_node]
            dest_x, dest_y, _ = self.board.labels_map[edge.to_node]
            if src_z != self.floor_number:  # TODO: Validator should verify that src_z == dest_z
                return
            draw_dotted_line(
                draw,
                ((src_x + 0.5) * SPACE_WIDTH, (src_y + 0.5) * SPACE_HEIGHT),
                ((dest_x + 0.5) * SPACE_WIDTH, (dest_y + 0.5) * SPACE_HEIGHT),
                fill='red',
                width=2,
            )

    def _highlight_space(self, x: int, y: int, outline_colors: Iterable[AttributeColor]) -> None:
        draw = ImageDraw.Draw(self.image)
        x0 = x * SPACE_WIDTH + 2
        y0 = y * SPACE_HEIGHT + 2
        x1 = x0 + SPACE_WIDTH - 4
        y1 = y0 + SPACE_HEIGHT - 4
        for outline_color, outline_side in outline_colors:
            if outline_side == 'all':
                draw.line(
                    [(x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)],
                    fill=outline_color,
                    width=3,
                )
            elif outline_side == 'bottom':
                draw.line(
                    [(x0, y1), (x1, y1)],
                    fill=outline_color,
                    width=3,
                )
            x0 += 1
            x1 -= 1
            y0 += 1
            y1 -= 1

    def build(self) -> Image.Image:
        """Return the image being constructed. This renderer should be
        considered consumed once this method has been called."""
        return self.image


def render_image(config: ConfigFile, board: Board, floor_number: int, floor: Floor) -> Image.Image:
    """Render the floor to an image file by drawing the layers in
    order."""
    renderer = Renderer(config, board, floor_number, floor)
    for layer in Layer:
        renderer.render_layer(layer)
    return renderer.build()


class DisplayedImageProducer(OutputProducer):
    """OutputProducer that outputs an image to a new on-screen window."""
    _floor_number: int

    def __init__(self, floor_number: int) -> None:
        self._floor_number = floor_number

    def produce_output(self, config: ConfigFile, board: Board) -> None:
        image = render_image(config, board, self._floor_number, board.floors[self._floor_number])
        image.show()


class SavedImageProducer(OutputProducer):
    """OutputProducer that outputs an image to the given file."""
    output_filename: str
    _floor_number: int

    def __init__(self, output_filename: str, floor_number: int) -> None:
        self.output_filename = output_filename
        self._floor_number = floor_number

    def produce_output(self, config: ConfigFile, board: Board) -> None:
        image = render_image(config, board, self._floor_number, board.floors[self._floor_number])
        image.save(self.output_filename)
