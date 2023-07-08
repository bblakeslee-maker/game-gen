import arcade
from ..types import GameState

class CutsceneView(arcade.View):
    ...


class CutsceneController:
    view: CutsceneView

    def __init__(self, state: GameState, is_done_callback):
        print("CutsceneController")
        self.done = is_done_callback
        self.view = CutsceneView()

        self.done()
