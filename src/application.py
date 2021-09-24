"""
Instantiate and launch the application itself.

Classes:

    ApplicationState
    Application

Functions:

    run()
"""

import pyglet
from pyglet.window import key
import enum


class ApplicationState(enum.Enum):
    """
    The different possible states for the Application.
    """
    MAIN_MENU = 0
    PLAY_MENU = 1
    LOBBY_MENU = 2
    IN_GAME = 3
    SETTINGS_MENU = 4


class Application:
    """
    Top level application manager, controls everything including the window and
    any events.
    """

    # Set default size to a 720p window
    DEFAULT_SIZE = DEFAULT_WIDTH, DEFAULT_HEIGHT = 1280, 720

    # For now we don't actually have a menu, so we just head straight into the
    # game here.
    current_state = ApplicationState.IN_GAME

    def __init__(self):
        """ Initialise the application: set up our window. """
        # Create our window
        self.window = pyglet.window.Window(
            caption="Hello, Window!",
            resizable=True,
            vsync=False,
            width=self.DEFAULT_WIDTH,
            height=self.DEFAULT_HEIGHT,
        )
        self.window.push_handlers(self)  # Register self as an event handler

        # Create our graphics batch, this means we only need to perform a
        # single draw-call per frame.
        self.batch = pyglet.graphics.Batch()

        # Schedule our update methods
        pyglet.clock.schedule(self.on_update)

    def on_draw(self):
        """ Called when the window needs to redraw. """
        self.window.clear()  # Clear the screen
        self.batch.draw()    # Draw the batch

    def on_key_press(self, symbol: int, modifiers: int):
        """ Called every time the user presses a key on the keyboard. """
        # If user pressed F11, toggle fullscreen
        if symbol == key.F11:
            # Set window's fullscreen to the opposite of the current value
            self.window.set_fullscreen(not self.window.fullscreen)

    def on_update(self, dt: float):
        """ Called every frame, dt is the time passed since the last frame. """
        pass  # Unused

    def run(self):
        """ Fire 'er up! """
        pyglet.app.run()  # This just starts the event loop

    def __del__(self):
        """ Application destructor. """
        # Unschedule any functions
        pyglet.clock.unschedule(self.on_update)


def run():
    """ Instantiates the Application class and runs the mainloop. """
    app = Application()
    app.run()
