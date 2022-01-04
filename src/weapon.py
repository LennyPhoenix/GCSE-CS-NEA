""" Abstract class for a weapon.


Classes:

    Weapon
"""

# For weapon stats
from dataclasses import dataclass
# For weapon types
from enum import auto, Enum

import pyglet

from .object2d import Object2D
from .zsprite import ZSprite


class WeaponType(Enum):
    MELEE = auto()
    # RANGED = auto() (unimplemented)


@dataclass
class WeaponStats:
    """ Weapon stats dataclass. """
    damage: float
    cooldown: float


@dataclass
class MeleeWeaponStats(WeaponStats):
    """ Melee weapon stats dataclass. """
    speed: float
    range: float


class Weapon(Object2D):
    """ Template for a weapon. """
    TYPE: WeaponType
    STATS: WeaponStats
    # Animations for each state
    IDLE: pyglet.image.AbstractImage
    USE: pyglet.image.AbstractImage

    ROTATION_AMOUNT = 30.0

    def __init__(
        self,
        batch: pyglet.graphics.Batch,
        group: pyglet.graphics.Group,
        parent=Object2D
    ):
        """ Initializes the weapon. """
        super().__init__(0, 0, parent)

        # Set up the sprite
        self.sprite = ZSprite(
            self.IDLE,
            self.global_x,
            self.global_y,
            # Position the sprite in front of the player
            -self.global_y+10,
            batch=batch,
            group=group,
            # Allows us to use float valus for the Z
            subpixel=True
        )
        self.sprite.rotation = self.ROTATION_AMOUNT

    def set_flipped(self, flipped: bool):
        """ Sets the sprite's flipped state. """
        if flipped:
            self.sprite.scale_x = 1  # Unflip the sprite
            self.sprite.rotation = self.ROTATION_AMOUNT
        else:
            self.sprite.scale_x = -1  # Flip the sprite
            self.sprite.rotation = -self.ROTATION_AMOUNT

    def on_fixed_update(self, dt: float):
        """ Updates the weapon's sprite. """
        self.sprite.update(
            self.global_x,
            self.global_y,
            -self.global_y+10
        )
