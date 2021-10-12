""" Contains type definition for Space.

Classes:

    Space
"""

from .aabb import AABB

from typing import Set

# Define as type hint
Space = Set[AABB]
