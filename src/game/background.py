import arcade

from game.drawable import Drawable

class Background(arcade.Section):
    def __init__(self, left, bottom, width, height, **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)
        self.background = Drawable(color = arcade.color.BLACK)

    def open(self, background):
        self.background = background

    def on_draw(self):
        self.background.draw(self.left, self.bottom, self.width, self.height)
