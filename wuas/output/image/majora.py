
"""Majora's Mask moon special case. Eventually, I'll generalize this into a proper API."""

from __future__ import annotations

from wuas.constants import Layer

from typing import TYPE_CHECKING
from PIL import Image, ImageDraw

if TYPE_CHECKING:
    from . import Renderer


MAJORAS_MOON_LAYER = Layer.GAP_OVERLAY


def render_moon(renderer: Renderer) -> None:
    board = renderer.board
    try:
        majora_value = int(board.get_meta('majora'))
    except KeyError:
        # No moon, nothing to draw
        return
    if majora_value == 0:
        return
    image: Image.Image = Image.open('majora.png')
    w, h = image.size
    if majora_value == 1:
        w //= 4
        h //= 4
    elif majora_value == 2:
        w //= 2
        h //= 2
    image = image.resize((w, h))
    imag_w, _ = renderer.image.size
    renderer.image.paste(image, (imag_w - w + 16, -16), image)
