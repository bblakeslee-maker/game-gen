#!/usr/bin/env python

"""
This program shows how to:
  * Display a sequence of screens in your game.  The "arcade.View"
    class makes it easy to separate the code for each screen into
    its own class.
  * This example shows the absolute basics of using "arcade.View".
    See the "different_screens_example.py" for how to handle
    screen-specific data.

Make a separate class for each view (screen) in your game.
The class will inherit from arcade.View. The structure will
look like an arcade.Window as each View will need to have its own draw,
update and window event methods. To switch a View, simply create a View
with `view = MyView()` and then use the "self.window.set_view(view)" method.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.view_screens_minimal
"""

import arcade

from game.director import Director

WIDTH = 800
HEIGHT = 600




def main():
    """ Startup """
    window = arcade.Window(WIDTH, HEIGHT, "GameGen")
    # window.setup()

    director = Director(window)
    director.start_game()


    arcade.run()


if __name__ == "__main__":
    main()
