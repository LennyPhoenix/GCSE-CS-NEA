""" Manage game processes and mechanisms.

Classes:

    GameManager
"""

import pyglet
import pymunk


class GameManager:
    """ The game manager, controls all game processes - such as physics - and
    contains the dungeon itself along with any entities.
    """

    # The time between each fixed update function call
    FIXED_UPDATE_TIMESTEP = 1/60

    def __init__(self):
        """ Game Manager initialiser: setup physics space and schedule physics
        update method.
        """
        self.physics_space = pymunk.Space()

        # Set up our physics update method
        pyglet.clock.schedule_interval(self.on_fixed_update,
                                       self.FIXED_UPDATE_TIMESTEP)

    def on_fixed_update(self, dt: float):
        """ Physics update method, called at a fixed speed independant of
        framerate.
        """
        self.physics_space.step(self.FIXED_UPDATE_TIMESTEP)

    def __del__(self):
        """ Game Manager destructor. """
        # Unschedule any scheduled methods
        pyglet.clock.unschedule(self.on_fixed_update)
