""" Physics bodies and collision utilities.

Functions:

    get_axis_collision_distances
    get_axis_collision_times
    get_collision_normals

Classes:

    CollisionData
    Body
"""

from __future__ import annotations  # NOTE: This is necessary below Python 3.10

from .aabb import AABB

from pyglet.math import Vec2

from dataclasses import dataclass
from typing import Optional, Set, Tuple


# TODO: Find a way to remove the need for this
@dataclass
class CollisionData:
    """ Collision data dump class. """
    collided: bool
    collision_time: float
    normals: Vec2


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


class Body(AABB):
    """ A moving bounding box in 2D space. Contains some helper methods for
    finding the nearest collision in the space, and resolving the collision.
    """

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
