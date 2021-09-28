""" Axis-aligned bounding box object used for collision detection and
resolution.

Classes:

    AABB
"""

# https://www.gamedev.net/articles/programming/general-and-gameplay-programming/swept-aabb-collision-detection-and-response-r3084/
# https://www.amanotes.com/post/using-swept-aabb-to-detect-and-process-collision
# TODO: Add docstrings and comments

from __future__ import annotations  # NOTE: This is necessary below Python 3.10

import pyglet

from typing import Tuple


class AABB:
    # TODO: Add get_broad_phase method
    # TODO: Figure out better way of doing offsets

    debug_rect: pyglet.shapes.Rectangle = None

    def __init__(self,
                 x: float,
                 y: float,
                 w: float,
                 h: float,
                 offset: Tuple[float, float] = (0, 0),
                 layer: int = 0xFFFFFFFF,
                 mask: int = 0xFFFFFFFF):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.offset = offset
        self.layer = layer
        self.mask = mask

    def __repr__(self) -> str:
        return f"AABB({self.x}, {self.y}, {self.w}, {self.h})"

    @property
    def position(self) -> Tuple[float, float]:
        return (self.x, self.y)

    @position.setter
    def position(self, new_position: Tuple[float, float]):
        self.x, self.y = new_position

    @property
    def extends(self) -> Tuple[float, float]:
        return (self.w, self.h)

    @extends.setter
    def extends(self, new_extends: Tuple[float, float]):
        self.w, self.h = new_extends

    def is_colliding_aabb(self, other: AABB) -> bool:
        return (
            self.x + self.offset[0] <= other.x + other.offset[0] + other.w
            and self.x + self.offset[0] + self.w >= other.x + other.offset[0]
            and self.y + self.offset[1] <= other.y + other.offset[1] + other.h
            and self.y + self.offset[1] + self.h >= other.y + other.offset[1]
        )

    def is_colliding_point(self, point: Tuple[float, float]) -> bool:
        return (
            self.x + self.offset[0] <= point[0]
            and point[0] <= self.x + self.offset[0] + self.w
            and self.y + self.offset[1] <= point[1]
            and point[1] <= self.y + self.offset[1] + self.h
        )

    def create_debug_rect(
        self,
        colour: Tuple[int, int, int] = (255, 255, 255),
        batch: pyglet.graphics.Batch = None,
        group: pyglet.graphics.Group = None
    ):
        self.debug_rect = pyglet.shapes.Rectangle(
            x=self.x,
            y=self.y,
            width=self.w,
            height=self.h,
            color=colour,
            batch=batch,
            group=group
        )
        self.debug_rect.anchor_position = (-self.offset[0], -self.offset[1])

    def update_debug_rect(
        self,
        offset: Tuple[float, float] = (0, 0)
    ):
        # NOTE: By calling _update_position manually we only need to update
        #       vertex coordinates once.
        self.debug_rect._x, self.debug_rect._y = self.position
        self.debug_rect._width, self.debug_rect._height = self.extends
        self.debug_rect._anchor_x = -self.offset[0]
        self.debug_rect._anchor_y = -self.offset[1]
        self.debug_rect._update_position()

    def __del__(self):
        if self.debug_rect is not None:
            self.debug_rect.delete()
