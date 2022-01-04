""" Objects in 2D space.

Classes:

    Object2D
"""

from __future__ import annotations  # NOTE: This is necessary below Python 3.10

# The pyglet library provides a Vector 2 class, we will use this to represent 2D positions
from pyglet.math import Vec2

# Import typing annotations that we will need:
# - Optional: The type may be the specified type OR None.
from typing import Optional
# Import weakref tools, used to store parent objects later.
from weakref import ref, ReferenceType as Ref


# Define the Object 2D as a class
class Object2D:
    """ An object in 2D space with an X and Y position. Supports parenting with
    global positioning.
    """

    # Store the parent as a weakref to avoid cyclic references
    # This is an issue that arises when two objects contain a reference to
    # each-other and stops them from being garbage-collected from memory.
    _parent: Optional[Ref[Object2D]] = None

    # `x` and `y` are floats to allow objects to travel in-between pixels, the parent
    # is optional.
    def __init__(self, x: float, y: float, parent: Optional[Object2D] = None):
        """ Initialise with local position and optionally a parent. """
        self.x = x
        self.y = y
        self.parent = parent

    # Create a helper property for accessing the position as a 2D vector
    @property
    def position(self) -> Vec2:
        """ A tuple of the local X and Y coordinates. """
        return Vec2(self.x, self.y)

    # Allow the `x` and `y` to be set from a 2D vector using a setter method
    @position.setter
    def position(self, new_position: Vec2):
        """ Assigns new position directly to local X and Y. """
        self.x, self.y = new_position

    # Helper property to calculate the global X position of the object
    @property
    def global_x(self) -> float:
        """ The global X position relative to world origin. """
        global_x = self.x  # Start with local X
        if self.parent is not None:
            global_x += self.parent.global_x  # Add parent's global position
        # Each parent will recursively add its own parent's global position,
        # until there are no more parents.
        return global_x

    # Helper method to set the X position, resulting in an intended global X.
    # This essentially works by doing the reverse of the getter method.
    @global_x.setter
    def global_x(self, new_global_x: float):
        """ Adjusts local X so that global X becomes the intended value. """
        x = new_global_x
        if self.parent is not None:
            x -= self.parent.global_x  # Subtract parent's global position
        self.x = x

    # Global Y position getter, see global_x.
    @property
    def global_y(self) -> float:
        """ The global Y position relative to world origin. """
        y = self.y
        if self.parent is not None:
            y += self.parent.global_y
        return y

    # Global Y position setter, see global_y.
    @global_y.setter
    def global_y(self, new_global_y: float):
        """ Adjusts local Y so that global Y becomes the intended value. """
        y = new_global_y
        if self.parent is not None:
            y -= self.parent.global_y
        self.y = y

    # Combines the global_x and global_y properties into one 2D vector.
    @property
    def global_position(self) -> Vec2:
        """ A tuple of the global X and Y coordinates. """
        return Vec2(self.global_x, self.global_y)

    # Just like the position setter, unpacks a 2D vector into individual
    # components and assigns them.
    @global_position.setter
    def global_position(self, new_global_position: Vec2):
        """ Assigns new global position to global X and Y, offsetting the local
        position.
        """
        self.global_x, self.global_y = new_global_position

    # Getter method for the object's parent in space. If the parent is not None
    # dereference the weakref and return the actual object.
    @property
    def parent(self) -> Optional[Object2D]:
        """ Returns the object's parent. If None, then the object is parented
        to the world origin.
        """
        if self._parent is not None:
            return self._parent()  # Dereference weakref
        else:
            return None

    # Setter method for the object's parent in space. Converts the object to a
    # weakref and stores it in the `_parent` attribute to avoid weakrefs.
    @parent.setter
    def parent(self, new_parent: Optional[Object2D]):
        """ Assigns a new parent to the object, which may be None to parent the
        object to the world origin.
        """
        if new_parent is not None:
            self._parent = ref(new_parent)  # Create new weakref
        else:
            self._parent = None
