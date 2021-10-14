""" The player game object.

Classes:

    Player
"""

from __future__ import annotations  # NOTE: This is necessary below Python 3.10

from .body import Body
from .camera import Camera
from .space import Space

import pyglet
from pyglet.math import Vec2
from pyglet.window import key

from typing import Optional
from weakref import ref, ReferenceType as Ref


class Player(Body):
    """ A physics body controllable by the user. """

    # Define the player's physics layer
    LAYER = 1 << 1
    # Define a nice debug colour to differentiate from other rects
    DEBUG_COLOUR = (107, 248, 255)
    # Define a default speed
    SPEED = 80

    # Store space as weakref to avoid cyclic references
    _space: Optional[Ref[Space]] = None

    def __init__(
        self,
        position: Vec2,
        space: Space,
        keys: key.KeyStateHandler,
        batch: pyglet.graphics.Batch,
    ):
        """ Initialise with position, a physics space, a key handler and a
        graphics batch.
        """
        super().__init__(
            *position,
            12, 8,
            layer=Player.LAYER,
            mask=Body.DEFAULT_LAYER,
        )

        # Create a camera object
        self.camera = Camera(6, 6, 1, parent=self)

        # Create a debug rect, we will use this until we set-up sprites
        self.create_debug_rect(
            Player.DEBUG_COLOUR,
            batch,
            self.camera
        )

        # Store space and key handler
        self.keys = keys
        self.space = space

    def on_fixed_update(self, dt: float):
        # Use user input to determine movement vector
        vx, vy = 0, 0
        if self.keys[key.W]:
            vy += 1
        if self.keys[key.A]:
            vx -= 1
        if self.keys[key.S]:
            vy -= 1
        if self.keys[key.D]:
            vx += 1

        # Normalise the vector, no speedy diagonal movement here!
        velocity = Vec2(vx, vy).normalize()
        # Multiply by speed and delta time to make movement frame-independant
        velocity *= Vec2(self.SPEED * dt, self.SPEED * dt)

        # Move the body...
        self.move_and_slide(self.space, velocity)
        # ...align to pixel grid...
        self.global_position = round(self.global_position)
        # ...and update our debug rect!
        self.update_debug_rect()

    @property
    def space(self) -> Optional[Space]:
        """ Returns the body's space. (May be None) """
        if self._space is not None:
            return self._space()  # Dereference weakref
        else:
            return None

    @space.setter
    def space(self, new_space: Optional[Space]):
        """ Assigns a new space to the body, use None to set to nothing."""
        if self.space is not None:
            self.space.remove(self)  # Remove from current space

        if new_space is not None:
            self._space = ref(new_space)  # Create new weakref
            self.space.add(self)  # Add to new space
        else:
            self._space = None
