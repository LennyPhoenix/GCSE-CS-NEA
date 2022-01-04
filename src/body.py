""" Movable AABBs in space.

Classes:

    Body
"""

from __future__ import annotations  # NOTE: This is necessary below Python 3.10

from .aabb import AABB
from .collision import (CollisionData, get_axis_collision_distances,
                        get_axis_collision_times, get_collision_normals)
from .object2d import Object2D
from .space import Space

from pyglet.math import Vec2

from typing import Optional


class Body(AABB):
    """ A moving bounding box in 2D space. Contains some helper methods for
    finding the nearest collision in the space, and resolving the collision.
    """

    def __init__(
        self,
        x: float,  # From `Object2D`
        y: float,  # From `Object2D`
        w: float,  # From `AABB`
        h: float,  # From `AABB`
        layer: int = AABB.DEFAULT_LAYER,  # From `AABB`
        mask: int = AABB.DEFAULT_LAYER,  # Use our default layer from before
        parent: Optional[Object2D] = None  # From `Object2D`
    ):
        super().__init__(x, y, w, h, layer, parent)  # Initialise AABB fields

        self.mask = mask

    def get_collision_data(self, other: AABB, velocity: Vec2) -> CollisionData:
        """ Get the collision data between this and another bounding box, using
        a given velocity.
        """

        # Get Collision Distances
        x_entry_dist, x_exit_dist = get_axis_collision_distances(
            self.global_x, self.w, velocity.x,
            other.global_x, other.w
        )
        y_entry_dist, y_exit_dist = get_axis_collision_distances(
            self.global_y, self.h, velocity.y,
            other.global_y, other.h
        )
        entry_distances = Vec2(x_entry_dist, y_entry_dist)

        # Get Collision Times
        x_entry_time, x_exit_time = get_axis_collision_times(
            x_entry_dist, x_exit_dist,
            velocity.x
        )
        y_entry_time, y_exit_time = get_axis_collision_times(
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
        normals = get_collision_normals(
            entry_times,
            entry_distances,
        ) if collided else Vec2(0, 0)

        # Return data
        return CollisionData(
            collided,
            # Use whichever is nearest to resolve ongoing collisions in the
            # neatest manner.
            entry_time if abs(entry_time) < abs(exit_time) else exit_time,
            normals,
        )

    def get_nearest_collision(
        self,
        space: Space,
        velocity: Vec2,
    ) -> Optional[CollisionData]:
        """ Finds the nearest collision in the space, if any. """
        broad_phase = self.get_broad_phase(velocity)
        closest_data: Optional[CollisionData] = None

        # Loop over every box in the space
        for other in space:
            # Check if a collision is possible
            if other is not self and self.mask & other.layer and broad_phase.is_colliding_aabb(other):
                # Get data
                data = self.get_collision_data(other, velocity)
                if (
                    # No collision yet
                    closest_data is None
                    # New collision is nearer
                    or data.collision_time < closest_data.collision_time
                ) and data.collided:  # Check there actually was a collision
                    closest_data = data

        return closest_data

    def move(self, space: Space, velocity: Vec2) -> Vec2:
        """ Moves as far as possible in one iteration, returning the remaining
        velocity calculated using the slide method.
        """
        nearest_collision = self.get_nearest_collision(space, velocity)
        if nearest_collision is None:
            self.position += velocity  # Move all the way

            new_velocity = Vec2(0, 0)  # No more velocity left over
        else:
            # Move to point of collision
            self.x += velocity.x * nearest_collision.collision_time
            self.y += velocity.y * nearest_collision.collision_time

            # Calculate dot product of normals and velocity
            dot_product = (
                velocity.x * nearest_collision.normals.y
                + velocity.y * nearest_collision.normals.x
            ) * (1-nearest_collision.collision_time)

            # Determine new velocity
            new_velocity = Vec2(
                dot_product * nearest_collision.normals.y,
                dot_product * nearest_collision.normals.x
            )

        return new_velocity

    def move_and_slide(
        self,
        space: Space,
        velocity: Vec2,
        max_bounce: int = 3,
    ):
        """ Repeatedly moves with the given velocity until it equals 0 or the
        maximum bounces in one frame have been reached.
        """
        counter = 0
        # Move until velocity is zero
        while velocity != Vec2(0, 0) and counter < max_bounce:
            velocity = self.move(space, velocity)
            counter += 1  # Increment max bounces counter
