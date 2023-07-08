import arcade
from ..game_types import GameState

class SetupView(arcade.View):
    def __init__(self, is_done_callback):
        super().__init__()
        self.done = is_done_callback
        self.time_elapsed = 0

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        self.clear()
        arcade.start_render()
        arcade.draw_text("Setup", 400, 300,
                         arcade.color.BLACK, font_size=30, anchor_x="center")

    def on_update(self, delta_time):
        self.time_elapsed += delta_time
        print(self.time_elapsed)
        if self.time_elapsed > 1.5:
            self.done()


class SetupController:
    view: SetupView

    def __init__(self, state: GameState, is_done_callback):
        print("SetupController")
        self.done = is_done_callback
        self.view = SetupView(is_done_callback)
