""" The player game object.

Classes:

    Player
"""

from __future__ import annotations  # NOTE: This is necessary below Python 3.10

# Import all our classes and methods we need
from . import weapons
from .body import Body
from .camera import Camera
from .space import Space
from .weapon import Weapon
from .zsprite import ZSprite

# Pyglet submodules
import pyglet
from pyglet.math import Vec2
from pyglet.window import key

# Enum for the state machine
from enum import auto, Enum
from typing import Optional
# Weakref for storing the physics space
from weakref import ref, ReferenceType as Ref


class Player(Body):
    """ A physics body controllable by the user. """

    # Resources
    SPRITE_SHEET = pyglet.resource.image("sprites/player.png")
    IMG_GRID = pyglet.image.ImageGrid(SPRITE_SHEET, 2, 4)
    IDLE = pyglet.image.Animation.from_image_sequence(
        IMG_GRID[:2],  # Take a slice of the image grid
        1/4,
    )
    MOVING = pyglet.image.Animation.from_image_sequence(
        IMG_GRID[4:8],  # Take a slice of the image grid
        1/8,
    )

    # Define the player's physics layer
    LAYER = 1 << 1
    # Define a nice debug colour to differentiate from other rects
    DEBUG_COLOUR = (107, 248, 255)
    # Define a default speed
    SPEED = 80

    # Dash
    DASH_SPEED = 4  # Initial Dash Speed
    DASH_CONTROL = 0.5
    DASH_LENGTH = 0.2
    DASH_COOLDOWN = 0.1
    dash_timer = 0
    dash_cooldown_timer = 0

    # State Machine
    class State(Enum):
        IDLE = auto()
        RUNNING = auto()
        DASHING = auto()
        DEFAULT = IDLE
    _state = State.DEFAULT

    # Movement
    input_vec = Vec2(0, 0)
    dash_velocity = Vec2(0, 0)

    # Sprite
    sprite: ZSprite

    # Weapon
    current_weapon: Weapon

    # Store space as weakref to avoid cyclic references
    _space: Optional[Ref[Space]] = None

    def __init__(
        self,
        position: Vec2,
        space: Space,
        keys: key.KeyStateHandler,
        batch: pyglet.graphics.Batch,
    ):
        """ Initialise with position, a physics space, a key handler and a
        graphics batch.
        """
        super().__init__(
            *position,
            12, 8,
            layer=Player.LAYER,
            mask=Body.DEFAULT_LAYER,
        )

        # Create a camera object
        self.camera = Camera(6, 6, 1, parent=self)

        # Create a debug rect, we will use this until we set-up sprites
        self.create_debug_rect(
            Player.DEBUG_COLOUR,
            batch,
            self.camera
        )

        # Create Sprite
        self.sprite = ZSprite(
            self.IDLE,
            self.global_x + self.w/2,
            self.global_y,
            -self.global_y,
            batch=batch, group=self.camera,
            subpixel=True
        )

        # Store space and key handler
        self.keys = keys
        self.space = space

        # Weapon
        self.current_weapon = weapons.Sword(
            batch,
            self.camera,
            self
        )
        self.current_weapon.position = (10, 8)

    def get_input(self) -> Vec2:
        # Use user input to determine movement vector
        vx, vy = 0, 0
        if self.keys[key.W]:
            vy += 1
        if self.keys[key.A]:
            vx -= 1
        if self.keys[key.S]:
            vy -= 1
        if self.keys[key.D]:
            vx += 1
        # Normalise the vector, no speedy diagonal movement here!
        return Vec2(vx, vy).normalize()

    def on_update(self, dt: float):
        """ Called every frame. """
        if self.state == self.State.DASHING:
            # Count down on the dash timer
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                # If it reached 0, stop dashing
                self.state = self.State.RUNNING
        else:
            # Count down the dash cooldown timer
            self.dash_cooldown_timer -= dt
            # Receive user input
            self.input_vec = self.get_input()
            # Determine state
            if self.input_vec == Vec2(0, 0):
                self.state = self.State.IDLE
            else:
                self.state = self.State.RUNNING

    def on_fixed_update(self, dt: float):
        """ Called every physics update. """
        # Determine player speed
        input = self.input_vec

        # Flip sprite and weapon based on player movement.
        # This could be simplified, but this works for now.
        if self.input_vec.x > 0:
            self.sprite.scale_x = 1
            self.current_weapon.x = 10
            self.current_weapon.set_flipped(True)
        elif self.input_vec.x < 0:
            self.sprite.scale_x = -1
            self.current_weapon.x = 2
            self.current_weapon.set_flipped(False)

        speed = self.SPEED * dt
        if self.state == self.State.DASHING:
            speed *= self.DASH_SPEED
            # Determine dash control
            dash_control = self.get_input()
            dash_control *= Vec2(self.DASH_CONTROL, self.DASH_CONTROL)
            input += dash_control
        # Multiply by speed and delta time to make movement frame-independant
        velocity = input * Vec2(speed, speed)

        # Move the body...
        self.move_and_slide(self.space, velocity)
        # ...align to pixel grid...
        self.global_position = round(self.global_position)
        # ...and update our debug rect!
        self.update_debug_rect()
        self.sprite.update(
            self.global_x + self.w/2,
            self.global_y,
            -self.global_y
        )

        # Propagate fixed update to weapon
        self.current_weapon.on_fixed_update(dt)

    def on_key_press(self, symbol: int, modifiers: int):
        """ Called every time the user presses a key. """
        can_dash = (
            symbol == key.SPACE  # Space is pressed
            and self.input_vec != Vec2(0, 0)  # We are moving
            and self.dash_cooldown_timer <= 0  # The cooldown is over
        )
        if can_dash:
            self.state = self.State.DASHING  # Start dashing
            self.dash_timer = self.DASH_LENGTH  # Reset the dash timer
            self.dash_cooldown_timer = self.DASH_COOLDOWN  # Reset cooldown

    @property
    def space(self) -> Optional[Space]:
        """ Returns the body's space. (May be None) """
        if self._space is not None:
            return self._space()  # Dereference weakref
        else:
            return None

    @space.setter
    def space(self, new_space: Optional[Space]):
        """ Assigns a new space to the body, use None to set to nothing."""
        if self.space is not None:
            self.space.remove(self)  # Remove from current space

        if new_space is not None:
            self._space = ref(new_space)  # Create new weakref
            self.space.add(self)  # Add to new space
        else:
            self._space = None

    @property
    def state(self) -> Player.State:
        return self._state

    @state.setter
    def state(self, new_state: Player.State):
        if new_state != self._state:
            self._state = new_state
            # Update the sprite to match the state
            if new_state == Player.State.IDLE:
                # Idle animation
                self.sprite.image = self.IDLE
            elif new_state == Player.State.RUNNING:
                # Running animation
                self.sprite.image = self.MOVING


# Set the player's images to use a centered X position
for img in Player.IMG_GRID:
    img.anchor_x = img.width / 2
