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

            new_velocity = Vec2(0, 0)
        else:
            self.x += velocity.x * nearest_collision.collision_time
            self.y += velocity.y * nearest_collision.collision_time

            dot_product = (
                velocity.x * nearest_collision.y_normal
                + velocity.y * nearest_collision.x_normal
            ) * (1-nearest_collision.collision_time)

            new_velocity = Vec2(
                dot_product * nearest_collision.y_normal,
                dot_product * nearest_collision.x_normal
            )

        return new_velocity

    def move_and_slide(
        self,
        space: Set[AABB],
        velocity: Vec2,
        max_bounce: int = 3,
    ):
        counter = 0
        while velocity != Vec2(0, 0) and counter < max_bounce:
            velocity = self.move(space, velocity)
            counter += 1
