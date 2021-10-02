""" Axis-aligned bounding box object used for collision detection and
resolution.

Classes:

    AABB
"""

# https://www.gamedev.net/articles/programming/general-and-gameplay-programming/swept-aabb-collision-detection-and-response-r3084/
# https://www.amanotes.com/post/using-swept-aabb-to-detect-and-process-collision
# TODO: Add docstrings and comments

from __future__ import annotations  # NOTE: This is necessary below Python 3.10

from .object2d import Object2D

import pyglet

from typing import Optional, Tuple


class AABB(Object2D):
    # TODO: Add get_broad_phase method

    debug_rect: pyglet.shapes.Rectangle = None

    def __init__(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        layer: int = 0xFFFFFFFF,
        mask: int = 0xFFFFFFFF,
        parent: Optional[Object2D] = None
    ):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.layer = layer
        self.mask = mask
        self.parent = parent

    @property
    def extends(self) -> Tuple[float, float]:
        return (self.w, self.h)

    @extends.setter
    def extends(self, new_extends: Tuple[float, float]):
        self.w, self.h = new_extends

    def is_colliding_aabb(self, other: AABB) -> bool:
        return (
            self.global_x <= other.global_x + other.w
            and self.global_x + self.w >= other.global_x
            and self.global_y <= other.global_y + other.h
            and self.global_y + self.h >= other.global_y
        )

    def is_colliding_point(self, point: Tuple[float, float]) -> bool:
        return (
            self.global_x <= point[0]
            and point[0] <= self.global_x + self.w
            and self.global_y <= point[1]
            and point[1] <= self.global_y + self.h
        )

    def create_debug_rect(
        self,
        colour: Tuple[int, int, int] = (255, 255, 255),
        batch: pyglet.graphics.Batch = None,
        group: pyglet.graphics.Group = None
    ):
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
        # NOTE: By calling _update_position manually we only need to update
        #       vertex coordinates once.
        self.debug_rect._x, self.debug_rect._y = self.global_position
        self.debug_rect._width, self.debug_rect._height = self.extends
        self.debug_rect._update_position()

    def __del__(self):
        if self.debug_rect is not None:
            self.debug_rect.delete()
