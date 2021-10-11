""" Physics bodies for collisions and movement.

Classes:

    Body
"""

from __future__ import annotations

from .aabb import AABB, CollisionData

from pyglet.math import Vec2

from typing import Optional, Set


class Body(AABB):
    """ A moving bounding box in 2D space. Contains some helper methods for
    finding the nearest collision in the space, and resolving the collision.
    """

    def get_nearest_collision(
        self,
        space: Set[AABB],
        velocity: Vec2,
    ) -> Optional[CollisionData]:
        """ Finds the nearest collision in the space, if any. """
        broad_phase = self.get_broad_phase(velocity)
        closest_data: Optional[CollisionData] = None

        # Loop over every box in the space
        for other in space:
            # Check if a collision is possible
            if other is not self and broad_phase.is_colliding_aabb(other):
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

    def move(self, space: Set[AABB], velocity: Vec2) -> Vec2:
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
        space: Set[AABB],
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
