""" Axis-aligned bounding box object used for collision detection and
resolution.

Classes:

    AABB
"""

# https://www.gamedev.net/articles/programming/general-and-gameplay-programming/swept-aabb-collision-detection-and-response-r3084/
# https://www.amanotes.com/post/using-swept-aabb-to-detect-and-process-collision

from __future__ import annotations  # NOTE: This is necessary below Python 3.10

from .object2d import Object2D

import pyglet
from pyglet.math import Vec2

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class CollisionData:
    """ Collision data dump class. """
    collided: bool
    collision_time: float
    normals: Vec2


class AABB(Object2D):
    """ An Axis-Aligned Bounding Box, essentially a rect in 2D space. """

    # The pyglet rect debug renderer
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
        """ Initialise with fields.
        The layer is a mask of 32 bits, representing the collision types of
        this box.
        The mask is another 32-bit mask, but this time representing the layers
        that this box can collide with.
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.layer = layer
        self.mask = mask
        self.parent = parent

    @property
    def extends(self) -> Vec2:
        """ Alias for (width, height) """
        return Vec2(self.w, self.h)

    @extends.setter
    def extends(self, new_extends: Vec2):
        """ Update width and height """
        self.w, self.h = new_extends

    def is_colliding_aabb(self, other: AABB) -> bool:
        """ Check if this bounding box intersects with another boundind box.
        Will check for layer mask.
        """
        return (
            self.mask & other.layer  # Check mask allows collision with other
            and self.global_x < other.global_x + other.w
            and self.global_x + self.w > other.global_x
            and self.global_y < other.global_y + other.h
            and self.global_y + self.h > other.global_y
        )

    def is_colliding_point(self, point: Vec2) -> bool:
        """ Check if this bounding box contains the given point. """
        return (
            self.global_x <= point.x
            and point.x <= self.global_x + self.w
            and self.global_y <= point.y
            and point.y <= self.global_y + self.h
        )

    def get_broad_phase(self, velocity: Vec2) -> AABB:
        """ Gets the broad phase for the bounding box, essentially the total
        area the bounding box could possibly move through during the step.
        """
        x = min(self.x, self.x + velocity.x)
        y = min(self.y, self.y + velocity.y)
        # Old method, calculates the maximum side, then subtracts new pos
        # w = max(self.x + self.w, self.x + self.w + velocity.x) - x
        # h = max(self.y + self.h, self.y + self.h + velocity.y) - y
        # New method, calculates the absolute of the velocity and adds it
        w = self.w + abs(velocity.x)
        h = self.h + abs(velocity.y)
        return AABB(
            x, y, w, h,
            parent=self.parent,
            mask=self.mask,
            layer=self.layer
        )

    @staticmethod
    def get_axis_collision_distances(
        p: float, w: float, v: float,
        op: float, ow: float
    ) -> Tuple[float, float]:
        """ Gets the distance to the entry and exit points of a collision on
        one axis.

        Parameters:

            p: float - Position of first object
            w: float - Width of first object
            v: float - Velocity of first object
            op: float - Position of other object
            ow: float - Width of other object

        Returns:

            Tuple of entry and exit distances.

            Tuple[float, float]
        """
        r_to_ol = op - (p + w)
        l_to_or = (op + ow) - p

        if v > 0:
            distance_entry = r_to_ol
            distance_exit = l_to_or
        else:
            distance_entry = l_to_or
            distance_exit = r_to_ol

        return (distance_entry, distance_exit)

    @staticmethod
    def get_axis_collision_times(
        distance_entry: float,
        distance_exit: float,
        v: float
    ) -> Tuple[float, float]:
        """ Gets the entry and exit times for a collision in 1 dimension.

        Parameters:

            distance_entry: float - Entry distance of first object to other.
            distance_exit: float - Exit distance of first object to other.
            v: float - Velocity of first object

        Returns:

            Tuple of entry and exit times.

            Tuple[float, float]
        """

        if v == 0:
            entry_time = -float("inf")
            exit_time = float("inf")
        else:
            entry_time = distance_entry / v
            exit_time = distance_exit / v

        return (entry_time, exit_time)

    @staticmethod
    def get_collision_normals(
        collided: bool,
        entry_times: Vec2,
        entry_distances: Vec2
    ) -> Vec2:
        """ Calculates the normals for a collision.

        Parameters:

            collided: bool - Whether there was a collision
            entry_times: Vec2 - The times until a collision on each axis.
            entry_distances: Vec2 - The distances until a collision on each
                                    axis.

        Returns:

            Vector of collision normals.

            Vec2
        """

        x_normal = 0
        y_normal = 0

        if collided:
            if entry_times.x > entry_times.y:
                if entry_distances.x < 0:
                    x_normal = 1
                else:
                    x_normal = -1
            else:
                if entry_distances.y < 0:
                    y_normal = 1
                else:
                    y_normal = -1

        return Vec2(x_normal, y_normal)

    def get_collision_data(self, other: AABB, velocity: Vec2) -> CollisionData:
        """ Get the collision data between this and another bounding box, using
        a given velocity.
        """

        # Get Collision Distances
        x_entry_dist, x_exit_dist = self.get_axis_collision_distances(
            self.global_x, self.w, velocity.x,
            other.global_x, other.w
        )
        y_entry_dist, y_exit_dist = self.get_axis_collision_distances(
            self.global_y, self.h, velocity.y,
            other.global_y, other.h
        )
        entry_distances = Vec2(x_entry_dist, y_entry_dist)

        # Get Collision Times
        x_entry_time, x_exit_time = self.get_axis_collision_times(
            x_entry_dist, x_exit_dist,
            velocity.x
        )
        y_entry_time, y_exit_time = self.get_axis_collision_times(
            y_entry_dist, y_exit_dist,
            velocity.y
        )
        entry_times = Vec2(x_entry_time, y_entry_time)

        # Use closest entry and furthest exit
        entry_time = max(x_entry_time, y_entry_time)
        exit_time = min(x_exit_time, y_exit_time)

        # Was there a collision?
        collided = not (
            # No motion
            entry_time > exit_time
            # Or collision already happened
            or exit_time <= 0
            # Or collision happens further than 1 time step away
            or entry_time > 1
        )

        # Get collision normals
        normals = self.get_collision_normals(
            collided,
            entry_times,
            entry_distances,
        )

        # Return data
        return CollisionData(
            collided,
            # Use whichever is nearest to resolve ongoing collisions in the
            # neatest manner.
            entry_time if abs(entry_time) < abs(exit_time) else exit_time,
            normals,
        )

    def create_debug_rect(
        self,
        colour: Tuple[int, int, int] = (255, 255, 255),
        batch: pyglet.graphics.Batch = None,
        group: pyglet.graphics.Group = None
    ):
        """ Initialise a pyglet debug rect renderer. """
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
        """ Update the debug rect renderer. """
        # NOTE: By calling _update_position manually we only need to update
        #       vertex coordinates once.
        self.debug_rect._x, self.debug_rect._y = self.global_position
        self.debug_rect._width, self.debug_rect._height = self.extends
        self.debug_rect._update_position()

    def __del__(self):
        """ Delete our renderer if it exists. """
        if self.debug_rect is not None:
            self.debug_rect.delete()
