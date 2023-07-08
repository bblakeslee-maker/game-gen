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

class DialogBox(arcade.Section):
    def __init__(self, left, bottom, width, height, **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)
        self.is_open = False
        self.content = []
        self.index = 0

        self.background = Drawable(color = arcade.color.RED)
        self.left = left
        self.bottom = bottom
        self.width = width
        self.height = height

        self._char_index = 0

    def finished(self):
        return self.index == len(self.content)

    def open(self, content):
        self.content = content
        self.index = 0
        self._char_index = 0
        self.is_open = True

    def next(self):
        if self.is_open and self.finished():
            self.close()
            return True

        text = self.content[self.index]
        print(self.content)
        if self._char_index == len(text):
            self.index += 1
            self._char_index = 0
            return True

        return False

    def close(self):
        self.is_open = False

    def on_draw(self):
        FONT_SIZE = 14
        PADDING = 4

        start_y = self.bottom + self.height - PADDING - FONT_SIZE
        start_x = self.left + PADDING
        if self.index < len(self.content) and self.is_open:
            self.background.draw(self.left, self.bottom, self.width, self.height)
            text = self.content[self.index]
            self._char_index = min(self._char_index + 1, len(text))
            arcade.draw_text(text[:self._char_index], start_x, start_y, arcade.color.WHITE, 14, multiline=True, width=self.width - 2 * PADDING)
