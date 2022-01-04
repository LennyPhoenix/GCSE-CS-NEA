""" Contains type definition for Space.

Classes:

    Space
"""

# Import the Axis-Aligned Bounding Box class, defined `aabb.py`
from .aabb import AABB

# Use a `Set`, as it is faster than a `List` and the space does not need to be
# sorted in any particular order.
from typing import Set

# Define as type hint
Space = Set[AABB]
