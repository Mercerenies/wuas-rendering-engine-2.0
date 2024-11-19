
"""Constants useful throughout this program."""

from enum import IntEnum

SPACE_WIDTH = 32
SPACE_HEIGHT = 32


class Layer(IntEnum):
    """Drawing spaces is done via layers, to make sure everything looks
    reasonable in the resulting image. Every space type has a layer
    intrinsic to it, which can be queried via get_layer. Spaces with a
    lower layer will draw first, allowing those with a higher layer to
    draw on top of them. The defined layers, in ascending order, are

    * VOID - The minimum layer. By definition, nothing is on this
      layer, and it appears behind everything else.

    * GAP - The layer of gaps (i.e. empty white impassible spaces) and
      similar background-ish elements.

    * GAP_OVERLAY - Layer for visual-only objects that appear in front
      of gaps but below mechanical spaces.

    * REGULAR - The layer of all spaces that do not have special
      drawing rules.

    * HIGHWAY - The layer on which highway lines are drawn.

    * HIGHWAY_SPACE - The layer on which spaces connected to the
      highway by highway lines are drawn.

    * TOKEN - No spaces draw on this layer. This is the layer of token
      objects, such as players and items, which draw on top of the
      space layer.

    """

    VOID = -999
    GAP = 0
    GAP_OVERLAY = 1
    REGULAR = 2
    HIGHWAY = 3
    HIGHWAY_SPACE = 4
    TOKEN = 999
