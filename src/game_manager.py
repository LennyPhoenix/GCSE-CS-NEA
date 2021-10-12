""" Manage game processes and mechanisms.

Classes:

    GameManager
"""

from __future__ import annotations

from .aabb import AABB
from .player import Player
from .space import Space

import pyglet
from pyglet.math import Vec2
from pyglet.window import key


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
        batch: pyglet.graphics.Batch,
        keys: key.KeyStateHandler
    ):
        """ Game Manager initialiser: schedule physics update method. """

        self.keys = keys

        self.space = set()

        self.player = Player(Vec2(0, 0), self.space, self.keys, batch)

        self.box_1 = AABB(120, 85, 30, 30)
        self.box_1.create_debug_rect(batch=batch)
        self.space.add(self.box_1)
        self.box_2 = AABB(100, 65, 30, 30)
        self.box_2.create_debug_rect(batch=batch)
        self.space.add(self.box_2)
        self.box_3 = AABB(140, 65, 30, 30)
        self.box_3.create_debug_rect(batch=batch)
        self.space.add(self.box_3)

        # Set up our physics update method
        pyglet.clock.schedule_interval(
            self.on_fixed_update,
            self.FIXED_UPDATE_TIMESTEP
        )

    def on_fixed_update(self, dt: float):
        """ Physics update method, called at a fixed speed independant of
        framerate.
        """
        self.player.on_fixed_update(dt)

    def __del__(self):
        """ Game Manager destructor. """
        # Unschedule any scheduled methods
        pyglet.clock.unschedule(self.on_fixed_update)
