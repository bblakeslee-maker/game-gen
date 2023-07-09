import arcade
from ..game_types import GameState

import game.dialog_box as dialog_box

class TextDumpView(arcade.View):
    def __init__(self, state: GameState, is_done_callback):
        super().__init__()
        self.state = state
        self.done = is_done_callback
        self.width = state.window_size[0]
        self.height = state.window_size[1]

        self.content = self.state.story_teller.prologue

        # Add sections for each of the areas:
        self.dialog_section = dialog_box.DialogBox(0,
                                                   0,
                                                   self.width,
                                                   self.height)
        self.dialog_section.set_callback(lambda: self.dialog_next())

        self.section_manager.add_section(self.dialog_section)

        self.dialog_section.open([self.content])

    def dialog_next(self):
        self.dialog_section.next()
        if self.dialog_section.finished():
            self.dialog_section.close()
            self.done()

    def on_update(self, delta_time: float):
        pass

    def on_draw(self):
        arcade.start_render()

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, _buttons: int, _modifiers: int):
        pass

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.dialog_next()

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        pass

    def on_mouse_enter(self, x: float, y: float):
        pass

    def on_mouse_leave(self, x: float, y: float):
        pass


class TextDumpController:
    view: TextDumpView

    def __init__(self, state: GameState, is_done_callback):
        print("TextDumpController")
        self.done = is_done_callback
        self.view = TextDumpView(state, is_done_callback)
