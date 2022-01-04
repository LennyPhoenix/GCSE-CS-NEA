""" Collision utility methods and classes.

Functions:

    get_axis_collision_distances
    get_axis_collision_times
    get_collision_normals

Classes:

    CollisionData
"""

from pyglet.math import Vec2

from dataclasses import dataclass
from typing import Tuple


@dataclass
class CollisionData:
    """ Collision data dump class. """
    collided: bool
    collision_time: float
    normals: Vec2


def get_axis_collision_distances(
    p1: float, w1: float, v1: float,
    p2: float, w2: float
) -> Tuple[float, float]:
    """ Gets the distance to the entry and exit points of a collision on
    one axis.

    Parameters:

        p1: float - Position of first object
        w1: float - Width of first object
        v1: float - Velocity of first object
        p2: float - Position of other object
        w2: float - Width of other object

    Returns:

        Tuple of entry and exit distances.

        Tuple[float, float]
    """
    # The distance from the right side of the first
    # object to the left side of the other object
    r_to_2l = p2 - (p1 + w1)
    # The distance from the left side of the first
    # object to the right side of the other object
    l_to_2r = (p2 + w2) - p1

    if v1 > 0:
        distance_entry = r_to_2l
        distance_exit = l_to_2r
    else:
        distance_entry = l_to_2r
        distance_exit = r_to_2l

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

    if v == 0:  # The object is not moving
        # It would take an infinite amount of time to collide
        entry_time = -float("inf")
        exit_time = float("inf")
    else:
        # v = d / t
        entry_time = distance_entry / v
        exit_time = distance_exit / v

    return (entry_time, exit_time)


def get_collision_normals(
    entry_times: Vec2,
    entry_distances: Vec2
) -> Vec2:
    """ Calculates the normals for a collision.

    Parameters:

        entry_times: Vec2 - The times until a collision on each axis.
        entry_distances: Vec2 - The distances until a collision on each
                                axis.

    Returns:

        Vector of collision normals.

        Vec2
    """

    x_normal = 0
    y_normal = 0

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
