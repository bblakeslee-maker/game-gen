import arcade
from ..types import GameState

class PrologueView(arcade.View):
    ...


class PrologueController:
    view: PrologueView

    def __init__(self, state: GameState, is_done_callback):
        print("PrologueController")
        self.done = is_done_callback
        self.view = PrologueView()

        self.done()

