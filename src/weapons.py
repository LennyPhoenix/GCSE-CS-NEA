""" All in game weapons.

Classes:

    Sword
"""

# Import weapon templates
from . import weapon

import pyglet


class Sword(weapon.Weapon):
    """ A sword for testing. """
    TYPE = weapon.WeaponType.MELEE
    STATS = weapon.MeleeWeaponStats(
        damage=10.0,
        cooldown=0.2,
        speed=1/2,
        range=32.0,
    )
    IDLE = pyglet.resource.image("sprites/sword.png")
    USE = pyglet.resource.image("sprites/sword.png")


# Set the sprite anchor points
Sword.IDLE.anchor_x = 8
Sword.IDLE.anchor_y = 5
