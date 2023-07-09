import arcade

from game.drawable import Drawable

class DialogBox(arcade.Section):
    def __init__(self, left, bottom, width, height, **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)
        self.is_open = False
        self.content = []
        self.index = 0

        self.background = Drawable(color = arcade.color.BLACK)
        self.left = left
        self.bottom = bottom
        self.width = width
        self.height = height

        self.font_size = 24
        self.padding = 50

        self.char_per_frame = 1

        self.callback = None

        self._char_index = 0

    def set_callback(self, callback):
        self.callback = callback

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
            return

        text = self.content[self.index]
        if self._char_index == len(text):
            self.index += 1
            self._char_index = 0

    def close(self):
        self.is_open = False

    def on_draw(self):
        start_y = self.bottom + self.height - self.padding - self.font_size
        start_x = self.left + self.padding
        if self.index < len(self.content) and self.is_open:
            self.background.draw(self.left, self.bottom, self.width, self.height)
            text = self.content[self.index]

            if self.char_per_frame < 1:
                self._char_index = len(text)
            else:
                self._char_index = min(self._char_index + self.char_per_frame, len(text))
            arcade.draw_text(text[:self._char_index], start_x, start_y, arcade.color.WHITE, self.font_size, multiline=True, width=self.width - 2 * self.padding)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.callback != None:
            self.callback()
