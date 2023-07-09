import arcade

class Drawable():
    def __init__(self, color=None, texture=None):
        self.color = color
        self.texture = texture

    def draw(self, left, bottom, width, height):
        if self.color:
            arcade.draw_rectangle_filled(left + width // 2, bottom + height // 2, width, height, self.color)
        elif self.texture:
            arcade.draw_texture_rectangle(left + width // 2, bottom + height // 2, width, height, self.texture)
        else:
            raise ValueError('Either color or texture must be specified')
