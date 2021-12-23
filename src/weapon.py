""" Abstract class for a weapon.


Classes:

    Weapon
"""

from dataclasses import dataclass
from enum import auto, Enum

import pyglet

from .object2d import Object2D
from .zsprite import y_to_z, ZSprite

class WeaponType(Enum):
    MELEE = auto()

@dataclass
class WeaponStats:
    damage: float
    cooldown: float


@dataclass
class MeleeWeaponStats(WeaponStats):
    speed: float
    range: float


class Weapon(Object2D):
    TYPE: WeaponType
    STATS: WeaponStats
    IDLE: pyglet.image.AbstractImage
    USE: pyglet.image.AbstractImage

    def __init__(
        self,
        batch: pyglet.graphics.Batch,
        group: pyglet.graphics.Group,
        parent = Object2D
    ):
        super().__init__(0, 0, parent)

        self.sprite = ZSprite(
            self.IDLE,
            self.global_x,
            self.global_y,
            y_to_z(self.global_y),
            batch=batch,
            group=group
        )

    def on_fixed_update(self, dt: float):
        self.sprite.update(
            self.global_x,
            self.global_y,
            y_to_z(self.global_y)
        )
