import arcade
import arcade.gui

import dialog_box
import cutscreen_view

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Dialog Box Example"

def main():
    window = arcade.Window(resizable=False)
    game = cutscreen_view.CutscreenView(SCREEN_WIDTH, SCREEN_HEIGHT)

    window.show_view(game)

    window.run()

if __name__ == "__main__":
    main()
