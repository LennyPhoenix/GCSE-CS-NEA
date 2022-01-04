""" Axis-aligned bounding box object used for collision detection and
resolution.

Classes:

    AABB
"""

# https://www.gamedev.net/articles/programming/general-and-gameplay-programming/swept-aabb-collision-detection-and-response-r3084/
# https://www.amanotes.com/post/using-swept-aabb-to-detect-and-process-collision

from __future__ import annotations  # NOTE: This is necessary below Python 3.10

# Import the previously defined `Object2D` class from the `object2d.py` file.
from .object2d import Object2D

# We perform some graphics handling here, so we need to import `pyglet` itself
import pyglet
# Use the `Vec2` class from pyglet's `math` module
from pyglet.math import Vec2

# Import typing annotations we will need
from typing import Optional, Tuple


# Define our `AABB` class
class AABB(Object2D):
    """ An Axis-Aligned Bounding Box, essentially a rect in 2D space. """

    # The default layer bitmask for AABBs
    # This is a simple bitshift operation returning 1, but we write it like
    # this in order to make it clear that it is a bitmask.
    DEFAULT_LAYER = 1 << 0

    # The pyglet rect debug renderer, None until a debug rect is created
    debug_rect: Optional[pyglet.shapes.Rectangle] = None

    def __init__(
        self,
        x: float,  # From `Object2D`
        y: float,  # From `Object2D`
        w: float,
        h: float,
        layer: int = DEFAULT_LAYER,  # Use our previously defined default layer
        parent: Optional[Object2D] = None  # From `Object2D`
    ):
        """ Initialise with fields.
        The layer is a mask of 32 bits, representing the collision types of
        this box.
        The mask is another 32-bit mask, but this time representing the layers
        that this box can collide with.
        """
        super().__init__(x, y, parent)  # Initialise the `Object2D` fields

        self.w = w
        self.h = h
        self.layer = layer

    # Similar to the `position` property, this is the getter for `w`
    # (width) and `h` (height) combined into a single 2D vector.
    @property
    def extends(self) -> Vec2:
        """ Alias for (width, height) """
        return Vec2(self.w, self.h)

    # Allow the `w` and `h` to be set from a 2D vector using a setter method
    @extends.setter
    def extends(self, new_extends: Vec2):
        """ Update width and height """
        self.w, self.h = new_extends

    def is_colliding_aabb(self, other: AABB) -> bool:
        """ Check if this bounding box intersects with another boundind box.
        Will check for layer mask.
        """
        # This boolean expression checks if the two bounding boxes are
        # intersecting by comparing their positions and extents.
        # See the following diagram:
        # https://static.wixstatic.com/media/ad6d77_bb25becfb6104aebad8cdfa2c696a3c8~mv2.png
        return (
            self.global_x < other.global_x + other.w
            and self.global_x + self.w > other.global_x
            and self.global_y < other.global_y + other.h
            and self.global_y + self.h > other.global_y
        )

    def is_colliding_point(self, point: Vec2) -> bool:
        """ Check if this bounding box contains the given point. """
        return (
            self.global_x <= point.x
            and point.x <= self.global_x + self.w
            and self.global_y <= point.y
            and point.y <= self.global_y + self.h
        )

    def get_broad_phase(self, transformation: Vec2) -> AABB:
        """ Gets the broad phase for the bounding box, essentially the total
        area the bounding box could possibly move through during the
        transformation.
        """
        # Calculate the bottom-left corner of the broad-phase:
        x = min(self.x, self.x + transformation.x)
        y = min(self.y, self.y + transformation.y)
        # Calculate the extent of the broad-phase:
        w = self.w + abs(transformation.x)
        h = self.h + abs(transformation.y)

        # Create a new AABB to represent the broad-phase and return it
        return AABB(
            x, y, w, h,
            parent=self.parent,
            layer=self.layer
        )

    def create_debug_rect(
        self,
        colour: Tuple[int, int, int] = (255, 255, 255),
        batch: Optional[pyglet.graphics.Batch] = None,
        group: Optional[pyglet.graphics.Group] = None
    ):
        """ Initialise a pyglet debug rect renderer. """
        self.debug_rect = pyglet.shapes.Rectangle(
            x=self.global_x,
            y=self.global_y,
            width=self.w,
            height=self.h,
            color=colour,
            batch=batch,
            group=group
        )

    def update_debug_rect(self):
        """ Update the debug rect renderer. """
        # NOTE: By calling _update_position manually we only need to update
        #       vertex coordinates once.
        self.debug_rect._x, self.debug_rect._y = self.global_position
        self.debug_rect._width, self.debug_rect._height = self.extends
        self.debug_rect._update_position()

    # This is necessary to perform some basic cleanup when the AABB is removed
    # from memory. If the debug rect is not None, we need to make sure we run
    # `delete` to remove it from the graphics batch and make it "disappear".
    def __del__(self):
        """ Delete our renderer if it exists. """
        if self.debug_rect is not None:
            self.debug_rect.delete()
