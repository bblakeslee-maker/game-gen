import arcade
from ..game_types import GameState

import game.dialog_box as dialog_box
from game.scenes.cutscene import Background

class TitleView(arcade.View):
    def __init__(self, state: GameState, is_done_callback):
        super().__init__()
        self.state = state
        self.done = is_done_callback
        self.width = state.window_size[0]
        self.height = state.window_size[1]

        self.content = self.state.story_teller.title

        self.time_elapsed = 0
        self.done_waiting = True #False

        self.bg_section = Background(0,
                                     0,
                                     self.width,
                                     self.height)

        background_path = self.state.image_generator.get_background('title-card')
        print(background_path)

        self.bg_section.open(dialog_box.Drawable(texture = arcade.load_texture(background_path)))
        self.section_manager.add_section(self.bg_section)


    def on_update(self, delta_time: float):
        self.time_elapsed += delta_time

        if self.time_elapsed > 5.0:
            self.done_waiting = True

    def on_draw(self):
        FONT_SIZE = 50

        arcade.start_render()

        # Assume that the title is 2 lines
        start_y = (self.height - FONT_SIZE) // 2 + FONT_SIZE
        arcade.draw_text(self.content, 0, start_y, arcade.color.WHITE, FONT_SIZE, width=self.width, align="center")

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.done_waiting:
            self.done()


class TitleController:
    view: TitleView

    def __init__(self, state: GameState, is_done_callback):
        print("TitleController")
        self.done = is_done_callback
        self.view = TitleView(state, is_done_callback)
