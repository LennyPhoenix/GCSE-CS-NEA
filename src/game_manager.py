""" Manage game processes and mechanisms.

Classes:

    GameManager
"""

from __future__ import annotations

# Import the components we need from earlier
from .aabb import AABB
from .player import Player
from .space import Space

import pyglet  # Graphics rendering library
from pyglet.math import Vec2  # 2D Vector class
from pyglet.window import key  # Makes references to keys easier


class GameManager:
    """ The game manager, controls all game processes - such as physics - and
    contains the dungeon itself along with any entities.
    """

    # The time between each fixed update function call
    FIXED_UPDATE_TIMESTEP = 1/60

    # Physics Space
    space: Space

    def __init__(
        self,
        batch: pyglet.graphics.Batch,  # The batch we need to draw to
        keys: key.KeyStateHandler  # The window key handler
    ):
        """ Game Manager initialiser: schedule physics update method. """

        self.keys = keys  # Store a reference to the key handler

        self.space = set()  # Initialise the physics space

        # Initialise the player in our testing environment
        self.player = Player(Vec2(0, 0), self.space, self.keys, batch)

        # Next we are going to define some boxes.
        # These will be arranged end-to-end, so we need to know the size
        # of each box.
        box_size = 30
        # The reason we do this is to check how smoothly the collision
        # system works. In an ideal world, the player should be able to move
        # against the seams of the boxes.
        self.box_1 = AABB(125, 85, box_size, box_size)
        self.box_1.create_debug_rect(
            batch=batch,
            group=self.player.camera  # Use the player's camera to display it
        )
        self.space.add(self.box_1)  # Add it to the physics space
        # Define our next box...
        self.box_2 = AABB(
            # Place it on the right side of the first box
            self.box_1.position.x + box_size,
            self.box_1.position.y,
            box_size,
            box_size
        )
        self.box_2.create_debug_rect(
            batch=batch,
            group=self.player.camera
        )
        self.space.add(self.box_2)
        # Define our third box...
        self.box_3 = AABB(
            # Place it on the right side of the second box
            self.box_2.position.x + box_size,
            self.box_2.position.y,
            box_size,
            box_size
        )
        self.box_3.create_debug_rect(
            batch=batch,
            group=self.player.camera
        )
        self.space.add(self.box_3)

        # Set up our physics update method
        pyglet.clock.schedule_interval(
            self.on_fixed_update,
            self.FIXED_UPDATE_TIMESTEP
        )

    def on_key_press(self, symbol: int, modifiers: int):
        """ Called every time the user presses a key on the keyboard. """
        # Send the event to the player
        self.player.on_key_press(symbol, modifiers)

    def on_resize(self, width: float, height: float):
        """ Called every time the window is resized. """
        # Send the event to the player's camera
        self.player.camera.on_window_resize(width, height)

    def on_update(self, dt: float):
        """ Called every frame, dt is time passed since last frame. """
        # Send the event to the player
        self.player.on_update(dt)

    def on_fixed_update(self, dt: float):
        """ Physics update method, called at a fixed speed independant of
        framerate.
        """
        # Send the event to the player
        self.player.on_fixed_update(dt)

    def __del__(self):
        """ Game Manager destructor. """
        # Unschedule any scheduled methods
        pyglet.clock.unschedule(self.on_fixed_update)
