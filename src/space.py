""" Contains type definition for Space.

Classes:

    Space
"""

from __future__ import annotations

from .aabb import AABB

from typing import NewType, Set

# Define as type hint
Space = NewType("Space", Set[AABB])
