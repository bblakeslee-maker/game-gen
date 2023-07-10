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
                                                   self.height,
                                                   sfx=False)
        self.dialog_section.set_callback(lambda: self.dialog_next())
        self.dialog_section.char_per_frame = 1
        self.dialog_section.open([self.content])


        # Add section for loading message
        self.loading_section = dialog_box.DialogBox(0,
                                                   0,
                                                   self.width,
                                                   100)
        self.loading_section.open(["Loading..."])

        self.loading_section.char_per_frame = -1


        self.section_manager.add_section(self.dialog_section)
        self.section_manager.add_section(self.loading_section)


    def dialog_next(self):
        if not self.dialog_section.finished():
            self.dialog_section.next()

        if self.dialog_section.finished() and \
                self.state.story_generation_future is not None and \
                self.state.story_generation_future.done():
            self.done()
            self.dialog_section.close()

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
