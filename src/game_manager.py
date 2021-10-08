""" Manage game processes and mechanisms.

Classes:

    GameManager
"""

from __future__ import annotations

from .aabb import AABB
from .body import Body

import pyglet
from pyglet.window import key

from typing import Set


class GameManager:
    """ The game manager, controls all game processes - such as physics - and
    contains the dungeon itself along with any entities.
    """

    # The time between each fixed update function call
    FIXED_UPDATE_TIMESTEP = 1/60

    # Physics Space
    space: Set[AABB]

    def __init__(self, batch, keys):
        """ Game Manager initialiser: schedule physics update method. """

        self.keys = keys

        self.space = set()

        self.body = Body(100, 95, 10, 10)
        self.body.create_debug_rect(batch=batch)
        self.space.add(self.body)
        self.box = AABB(120, 85, 30, 30)
        self.box.create_debug_rect(batch=batch)
        self.space.add(self.box)

        # Set up our physics update method
        pyglet.clock.schedule_interval(
            self.on_fixed_update,
            self.FIXED_UPDATE_TIMESTEP
        )

    def on_fixed_update(self, dt: float):
        """ Physics update method, called at a fixed speed independant of
        framerate.
        """
        vx, vy = 0, 0

        if self.keys[key.W]:
            vy += 10
        if self.keys[key.A]:
            vx -= 10
        if self.keys[key.S]:
            vy -= 10
        if self.keys[key.D]:
            vx += 10

        velocity = pyglet.math.Vec2(vx * dt, vy * dt)
        self.body.move(self.space, velocity)

        self.body.update_debug_rect()

    def __del__(self):
        """ Game Manager destructor. """
        # Unschedule any scheduled methods
        pyglet.clock.unschedule(self.on_fixed_update)
