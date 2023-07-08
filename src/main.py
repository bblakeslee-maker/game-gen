import arcade
import arcade.gui

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Dialog Box Example"

class Drawable():
    def __init__(self, color=None, texture=None):
        self.color = color
        self.texture = texture

    def draw(self, center_x, center_y, width, height):
        if self.color:
            arcade.draw_rectangle_filled(center_x, center_y, width, height, self.color)
        elif self.texture:
            arcade.draw_texture_rectangle(center_x, center_y, width, height, self.texture)
        else:
            raise ValueError('Either color or texture must be specified')

class DialogBox():
    def __init__(self, content, center_x, center_y, width, height):
        self.is_open = False
        self.content = content
        self.index = 0

        self.background = Drawable(color = arcade.color.RED)
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height

        self._char_index = 0

    def open(self):
        self.is_open = True

    def next(self):
        if self.index == len(self.content):
            self.close()
            return

        text = self.content[self.index]
        if self._char_index == len(text):
            self.index += 1
            self._char_index = 0

    def close(self):
        self.is_open = False

    def draw(self):
        FONT_SIZE = 14
        PADDING = 4

        start_y = self.center_y + self.height // 2 - FONT_SIZE - PADDING
        start_x = self.center_x - self.width // 2 + PADDING
        if self.index < len(self.content) and self.is_open:
            self.background.draw(self.center_x, self.center_y, self.width, self.height)
            text = self.content[self.index]
            self._char_index = min(self._char_index + 1, len(text))
            arcade.draw_text(text[:self._char_index], start_x, start_y, arcade.color.WHITE, 14, multiline=True, width=self.width)


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        dialog_text = ["Hello", "Welcome to my Game where I show you the world that exists only in our minds or maybe in our hearts but that doesn't matter anymore."]
        self.dialog_box = DialogBox(dialog_text, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 600, 300)
        self.dialog_box.background = Drawable(texture = arcade.load_texture("resource/dialog_box.png"))
        self.dialog_box.open()

    def on_draw(self):
        arcade.start_render()
        self.dialog_box.draw()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        self.dialog_box.next()


def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()

if __name__ == "__main__":
    main()
