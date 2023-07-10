import arcade
from ..game_types import GameState

from game.drawable import Drawable
from game.mouse_section import MouseSection
from game.background import Background

class Darkness(arcade.Section):
    def __init__(self, left, bottom, width, height, **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)
        self.left = left
        self.bottom = bottom
        self.width = width
        self.height = height
        self.background = Drawable(color = [0, 0, 0, 160])

    def set_callback(self, callback):
        self.callback = callback

    def on_draw(self):
        self.background.draw(self.left, self.bottom, self.width, self.height)

class TitleText(arcade.Section):
    def __init__(self, left, bottom, width, height, **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)
        self.content = ""

        self.left = left
        self.bottom = bottom
        self.width = width
        self.height = height

        self.font_size = 50
        self.padding = 50

    def set_callback(self, callback):
        self.callback = callback

    def on_draw(self):
        start_y = self.height // 2 - self.font_size

        arcade.draw_text(
                self.content,
                self.padding, start_y,
                arcade.color.WHITE,
                self.font_size,
                multiline=True,
                width=self.width - 2 * self.padding,
                align="center")

class TitleView(arcade.View):
    def __init__(self, state: GameState, is_done_callback, ending=False):
        super().__init__()
        self.state = state
        self.done = is_done_callback
        self.width = state.window_size[0]
        self.height = state.window_size[1]

        self.time_elapsed = 0
        self.done_waiting = False

        self.mouse_section = MouseSection(0,
                                          0,
                                          self.width,
                                          self.height,
                                          on_mouse_press=lambda: self.dialog_next())

        self.bg_section = Background(0,
                                     0,
                                     self.width,
                                     self.height)

        self.darkness_section = Darkness(0,
                                         0,
                                         self.width,
                                         self.height)

        self.title_section = TitleText(0,
                                       0,
                                       self.width,
                                       self.height)

        if ending:
            self.title_section.content = "The End"
        else:
            self.title_section.content = self.state.story_teller.title

        background_path = self.state.image_generator.get_background('title-card')

        self.bg_section.open(Drawable(texture = arcade.load_texture(background_path)))
        self.section_manager.add_section(self.mouse_section)
        self.section_manager.add_section(self.bg_section)
        self.section_manager.add_section(self.darkness_section)
        self.section_manager.add_section(self.title_section)

    def on_update(self, delta_time: float):
        self.time_elapsed += delta_time

        if self.time_elapsed > 5.0:
            self.done_waiting = True

    def on_draw(self):
        arcade.start_render()

    def dialog_next(self):
        if self.done_waiting:
            self.done()


class TitleController:
    view: TitleView

    def __init__(self, state: GameState, is_done_callback, ending=False):
        print("TitleController")
        self.done = is_done_callback
        self.view = TitleView(state, is_done_callback, ending=ending)
