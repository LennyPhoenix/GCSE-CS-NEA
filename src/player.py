""" The player game object.

Classes:

    Player
"""

from __future__ import annotations  # NOTE: This is necessary below Python 3.10

from .body import Body
from .space import Space

import pyglet
from pyglet.math import Vec2
from pyglet.window import key

from typing import Optional
from weakref import ref, ReferenceType as Ref


class Player(Body):
    # TODO: Add camera group

    LAYER = 1 << 1
    DEBUG_COLOUR = (107, 248, 255)

    # Store space as weakref to avoid cyclic references
    _space: Optional[Ref[Space]] = None

    def __init__(
        self,
        position: Vec2,
        space: Space,
        keys: key.KeyStateHandler,
        batch: pyglet.graphics.Batch,
    ):
        super().__init__(
            position.x, position.y,
            12, 8,
            layer=Player.LAYER,
            mask=Body.DEFAULT_LAYER,
        )
        self.create_debug_rect(Player.DEBUG_COLOUR, batch)

        self.keys = keys
        self.space = space

    def on_fixed_update(self, dt: float):
        vx, vy = 0, 0
        if self.keys[key.W]:
            vy += 1
        if self.keys[key.A]:
            vx -= 1
        if self.keys[key.S]:
            vy -= 1
        if self.keys[key.D]:
            vx += 1
        velocity = Vec2(vx, vy).normalize()
        velocity = velocity * Vec2(50 * dt, 50 * dt)

        self.move_and_slide(self.space, velocity)
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
            self.space.remove(self)

        if new_space is not None:
            self._space = ref(new_space)  # Create new weakref
            self.space.add(self)
        else:
            self._space = None
