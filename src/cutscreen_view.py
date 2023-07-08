import arcade

import dialog_box

class CutscreenEvent():
    def __init__(self, dialog, portrait, side, background):
        self.dialog = dialog
        self.portrait = portrait
        self.portrait_side = side
        self.background = background

class Portrait(arcade.Section):
    def __init__(self, left, bottom, width, height, **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)
        self.background = None
        self.is_open = False

    def open(self, background):
        print("open")
        self.background = background
        self.is_open = True

    def close(self):
        self.background = None
        self.is_open = False

    def on_draw(self):
        if self.is_open:
            self.background.draw(self.left, self.bottom, self.width, self.height)


class CutscreenView(arcade.View):
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height

        self.content = \
            [CutscreenEvent(["Hello", "world", "Very long line of text that demonstrates the single character per frame drawing."], dialog_box.Drawable(color = arcade.color.BLUE), 0, None),
             CutscreenEvent(["Hello 2", "world 2"], dialog_box.Drawable(color = arcade.color.GREEN), 1, None)]
        self.index = 0

        self.dialog_height = 100
        self.portrait_width = 100
        self.portrait_height = 100

        self.portrait_side = 0

        # Add sections for each of the areas:
        self.bg_section = arcade.Section(0,
                                         height,
                                         self.width,
                                         self.height - self.dialog_height)

        self.dialog_section = dialog_box.DialogBox(0,
                                                   0,
                                                   self.width,
                                                   self.dialog_height)

        self.left_char_portrait_section = Portrait(0,
                                                   self.dialog_section.height,
                                                   self.portrait_width,
                                                   self.portrait_height)

        self.right_char_portrait_section = Portrait(self.width - self.portrait_width,
                                                    self.dialog_section.height,
                                                    self.portrait_width,
                                                    self.portrait_height)

        self.section_manager.add_section(self.bg_section)
        self.section_manager.add_section(self.dialog_section)
        self.section_manager.add_section(self.left_char_portrait_section)
        self.section_manager.add_section(self.right_char_portrait_section)

        event = self.content[self.index]
        self.dialog_section.open(event.dialog)
        self.left_char_portrait_section.open(event.portrait)

    def set_content(self, content):
        self.content = content
        self.index = 0

    def finished(self):
        return self.index == len(self.content)

    def next(self):
        self.index += 1
        if self.finished():
            return

        event = self.content[self.index]

        self.dialog_section.close()
        self.dialog_section.open(event.dialog)

        self.portrait_side = 1 - self.portrait_side
        self.left_char_portrait_section.close()
        self.right_char_portrait_section.close()

        if self.portrait_side == 0:
            self.left_char_portrait_section.open(event.portrait)

        if self.portrait_side == 1:
            self.right_char_portrait_section.open(event.portrait)

    def on_update(self, delta_time: float):
        pass

    def on_draw(self):
        arcade.start_render()

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, _buttons: int, _modifiers: int):
        pass

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.dialog_section.next()
        if self.dialog_section.finished():
            self.next()

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        pass

    def on_mouse_enter(self, x: float, y: float):
        pass

    def on_mouse_leave(self, x: float, y: float):
        pass
