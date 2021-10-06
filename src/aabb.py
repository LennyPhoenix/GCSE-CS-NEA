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
from pyglet.math import Vec2

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class CollisionData:
    collided: bool
    x_entry: float
    x_exit: float
    x_normal: float
    y_entry: float
    y_exit: float
    y_normal: float
    collision_time: float


class AABB(Object2D):
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
    def extends(self) -> Vec2:
        return Vec2(self.w, self.h)

    @extends.setter
    def extends(self, new_extends: Vec2):
        self.w, self.h = new_extends

    def is_colliding_aabb(self, other: AABB) -> bool:
        return (
            self.global_x <= other.global_x + other.w
            and self.global_x + self.w >= other.global_x
            and self.global_y <= other.global_y + other.h
            and self.global_y + self.h >= other.global_y
        )

    def is_colliding_point(self, point: Vec2) -> bool:
        return (
            self.global_x <= point.x
            and point.x <= self.global_x + self.w
            and self.global_y <= point.y
            and point.y <= self.global_y + self.h
        )

    def get_broad_phase(self, velocity: Vec2) -> AABB:
        x = min(self.x, self.x + velocity.x)
        y = min(self.y, self.y + velocity.y)
        # Old method, calculates the maximum side, then subtracts new pos
        # w = max(self.x + self.w, self.x + self.w + velocity.x) - x
        # h = max(self.y + self.h, self.y + self.h + velocity.y) - y
        # New method, calculates the absolute of the velocity and adds it
        w = self.w + abs(velocity.x)
        h = self.h + abs(velocity.y)
        return AABB(x, y, w, h, parent=self.parent)

    def get_collision_data(self, other: AABB, velocity: Vec2) -> CollisionData:
        # Hey! This code is awful! Its slow, and basically just dumps the
        # collision data for the user to deal with themself.
        # TODO: Extract out into individual functions, preferably with each
        #       axis.

        # Determine exit and entry points in inverse time
        if velocity.x > 0:
            x_inv_entry = other.global_x - (self.global_x + self.w)
            x_inv_exit = (other.global_x + other.w) - self.global_x
        else:
            x_inv_entry = (other.global_x + other.w) - self.global_x
            x_inv_exit = other.global_x - (self.global_x + self.w)

        if velocity.y > 0:
            y_inv_entry = other.global_y - (self.global_y + self.h)
            y_inv_exit = (other.global_y + other.h) - self.global_y
        else:
            y_inv_entry = (other.global_y + other.h) - self.global_y
            y_inv_exit = other.global_y - (self.global_y + self.h)

        # Calculate actual exit and entry times
        if velocity.x == 0:
            x_entry = -float("inf")
            x_exit = float("inf")
        else:
            x_entry = x_inv_entry / velocity.x
            x_exit = x_inv_exit / velocity.x

        if velocity.y == 0:
            y_entry = -float("inf")
            y_exit = float("inf")
        else:
            y_entry = y_inv_entry / velocity.y
            y_exit = y_inv_exit / velocity.y

        # Use closest entry and furthest exit
        entry_time = min(x_entry, y_entry)
        exit_time = max(x_exit, y_exit)

        # Calculate normals
        if (
            entry_time > exit_time
            or (x_entry < 0 and y_entry < 0)
            or x_entry > 1 or y_entry > 1
        ):
            collided = False
            x_normal = 0.0
            y_normal = 0.0
        else:
            collided = True
            if x_entry > y_entry:
                if x_inv_entry < 0:
                    x_normal = 1
                    y_normal = 0
                else:
                    x_normal = -1
                    y_normal = 0
            else:
                if y_inv_entry < 0:
                    x_normal = 0
                    y_normal = 1
                else:
                    x_normal = 0
                    y_normal = -1

        # Return data
        return CollisionData(
            collided,
            x_entry, x_exit, x_normal,
            y_entry, y_exit, y_normal,
            entry_time
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
