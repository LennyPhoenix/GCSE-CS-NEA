""" All in game weapons.

Classes:

    Sword
"""

from . import weapon

import pyglet


class Sword(weapon.Weapon):
    TYPE = weapon.WeaponType.MELEE
    STATS = weapon.MeleeWeaponStats(
        damage = 10.0,
        cooldown = 0.2,
        speed = 1 / 2,
        range = 32.0,
    )
    IDLE = pyglet.resource.image("sprites/player.png")
    USE = pyglet.resource.image("sprites/player.png")
