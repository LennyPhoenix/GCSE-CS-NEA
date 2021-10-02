""" Objects in 2D space.

Classes:

    Object2D
"""

from __future__ import annotations  # NOTE: This is necessary below Python 3.10

from typing import Optional, Tuple
from weakref import ref, ReferenceType as Ref


class Object2D:
    """ An object in 2D space with an X and Y position. Supports parenting with
    global positioning.
    """

    # Store the parent as a weakref to avoid cyclic references
    _parent: Optional[Ref[Object2D]] = None

    def __init__(self, x: float, y: float, parent: Optional[Object2D] = None):
        """ Initialise with local position and optionally a parent. """
        self.x = x
        self.y = y
        self.parent = parent

    @property
    def position(self) -> Tuple[float, float]:
        """ A tuple of the local X and Y coordinates. """
        return (self.x, self.y)

    @position.setter
    def position(self, new_position: Tuple[float, float]):
        """ Assigns new position directly to local X and Y. """
        self.x, self.y = new_position

    @property
    def global_x(self) -> float:
        """ The global X position relative to world origin. """
        global_x = self.x  # Start with local X
        if self.parent is not None:
            global_x += self.parent.global_x  # Add parent's global position
        # Each parent will recursively add its own parent's global position,
        # until there are no more parents.
        return global_x

    @global_x.setter
    def global_x(self, new_global_x: float):
        """ Adjusts local X so that global X becomes the intended value. """
        x = new_global_x
        if self.parent is not None:
            x -= self.parent.global_x  # Subtract parent's global position
        self.x = x

    @property
    def global_y(self) -> float:
        """ The global Y position relative to world origin. """
        y = self.y
        if self.parent is not None:
            y += self.parent.global_y
        return y

    @global_y.setter
    def global_y(self, new_global_y: float):
        """ Adjusts local Y so that global Y becomes the intended value. """
        y = new_global_y
        if self.parent is not None:
            y -= self.parent.global_y
        self.y = y

    @property
    def global_position(self) -> Tuple[float, float]:
        """ A tuple of the global X and Y coordinates. """
        return (self.global_x, self.global_y)

    @global_position.setter
    def global_position(self, new_global_position: Tuple[float, float]):
        """ Assigns new global position to global X and Y, offsetting the local
        position.
        """
        self.global_x, self.global_y = new_global_position

    @property
    def parent(self) -> Optional[Object2D]:
        """ Returns the object's parent. If None, then the object is parented
        to the world origin.
        """
        if self._parent is not None:
            return self._parent()  # Dereference weakref
        else:
            return None

    @parent.setter
    def parent(self, new_parent: Optional[Object2D]):
        """ Assigns a new parent to the object, which may be None to parent the
        object to the world origin.
        """
        if new_parent is not None:
            self._parent = ref(new_parent)  # Create new weakref
        else:
            self._parent = None
