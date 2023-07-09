import arcade
import arcade.gui

from game.director import Director

WIDTH = 1200
HEIGHT = 900

def main():
    """ Startup """
    window = arcade.Window(WIDTH, HEIGHT, "GameGen")
    # window.setup()

    director = Director(window)
    director.start_game()

    arcade.run()

if __name__ == "__main__":
    main()
