""" Physics bodies for collisions and movement.

Classes:

    Body
"""

# TODO: Add documentation

from __future__ import annotations

from .aabb import AABB, CollisionData

from pyglet.math import Vec2

from typing import Optional, Set


class Body(AABB):
    # TODO: Add move_and_slide method

    def get_nearest_collision(
        self,
        space: Set[AABB],
        velocity: Vec2,
    ) -> Optional[CollisionData]:
        broad_phase = self.get_broad_phase(velocity)
        closest_data: Optional[CollisionData] = None

        for other in space:
            if other is not self and broad_phase.is_colliding_aabb(other):
                data = self.get_collision_data(other, velocity)
                if (
                    closest_data is None
                    or data.collision_time < closest_data.collision_time
                ) and data.collided:
                    closest_data = data

        return closest_data

    def move(self, space: Set[AABB], velocity: Vec2) -> Vec2:
        nearest_collision = self.get_nearest_collision(space, velocity)
        if nearest_collision is None:
            self.position += velocity
        else:
            self.x += velocity.x * nearest_collision.collision_time
            self.y += velocity.y * nearest_collision.collision_time

        # TODO: Figure out left-over velocity

        return Vec2(0, 0)
