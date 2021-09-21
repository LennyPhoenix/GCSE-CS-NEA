"""
Instantiate and launch the application itself.

Classes:

    Application

Functions:

    run()
"""

import pyglet


class Application:
    """
    Top level application manager, controls everything including the window and
    any events.
    """

    # Set default size to a 720p window
    DEFAULT_SIZE = DEFAULT_WIDTH, DEFAULT_HEIGHT = 1280, 720

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

    def on_draw(self):
        """ Called when the window needs to redraw. """
        self.window.clear()  # Clear the screen
        self.batch.draw()    # Draw the batch

    def run(self):
        """ Fire 'er up! """
        pyglet.app.run()  # This just starts the event loop


def run():
    """ Instantiates the Application class and runs the mainloop. """
    app = Application()
    app.run()
