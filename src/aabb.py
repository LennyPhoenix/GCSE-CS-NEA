""" Axis-aligned bounding box object used for collision detection and
resolution.

Classes:

    AABB
"""

# TODO: Add docstrings and comments

from typing import Tuple


class AABB:
    # TODO: Add is_colliding method
    # TODO: Add get_broad_phase method
    # TODO: Add create/update_debug_rect method

    def __init__(self, x: float, y: float, w: float, h: float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

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
