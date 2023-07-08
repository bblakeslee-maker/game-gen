import arcade
from ..types import GameState



class BattleView(arcade.View):
    ...


class BattleController:
    view: BattleView

    def __init__(self, state: GameState, is_done_callback):
        print("BattleController")
        self.done = is_done_callback
        self.view = BattleView()

        self.done()



