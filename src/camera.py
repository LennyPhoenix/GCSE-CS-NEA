""" Camera system using graphics groups.

Classes:

    Camera
"""

from .object2d import Object2D

import pyglet
from pyglet.graphics import Group
from pyglet.math import Vec2

from typing import Optional


class Camera(Group):
    """ Pyglet graphics group emulating the behaviour of a camera in 2D space.
    """

    # Define a target viewport resolution
    VIEW_RESOLUTION = Vec2(480, 270)

    # Use an Object2D for the camera position
    position: Object2D
    # Define a starting window size, this will be immediately overwritten by
    # the on_resize event
    window_size = Vec2(0, 0)

    def __init__(
        self,
        x: float, y: float,  # Position
        zoom: float = 1.0,
        parent: Optional[Object2D] = None,
        parent_group: Optional[Group] = None
    ):
        """ Initialise group with parent, zoom and position. """
        super().__init__(parent_group)
        self.zoom = zoom
        # Set up a Object 2D as a position anchor
        self.position = Object2D(x, y, parent)

    def on_window_resize(self, width: float, height: float):
        """ Called (through GameManager) every time the window is resized. """
        # Store window size
        self.window_size = Vec2(width, height)

    def get_viewport_scale(self) -> float:
        """ Get the scale required to resize the viewport to the intended size.

        Use min() here to find the smaller of the two axis' zooms.
        """
        return min(
            self.window_size.x / self.VIEW_RESOLUTION.x,
            self.window_size.y / self.VIEW_RESOLUTION.y
        )

    def set_state(self):
        """ Apply zoom and camera offset to view matrix. """
        # Calculate the total zoom amount
        zoom = self.get_viewport_scale() * self.zoom
        # Move the viewport
        pyglet.gl.glTranslatef(
            self.window_size.x/2 - self.position.global_x * zoom,
            self.window_size.y/2 - self.position.global_y * zoom,
            0
        )
        # Scale the viewport
        pyglet.gl.glScalef(zoom, zoom, 1)

    def unset_state(self):
        """ Revert zoom and camera offset from view matrix. """
        # Do the inverse of `set_state`
        zoom = self.get_viewport_scale() * self.zoom
        pyglet.gl.glScalef(1 / zoom, 1 / zoom, 1)
        pyglet.gl.glTranslatef(
            self.position.global_x * zoom - self.window_size.x/2,
            self.position.global_y * zoom - self.window_size.y/2,
            0
        )
