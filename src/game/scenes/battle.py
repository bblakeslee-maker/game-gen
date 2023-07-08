import arcade


class BattleView(arcade.View):
    ...


class BattleController:
    view: BattleView

    def __init__(self, is_done_callback):
        print("BattleController")
        self.done = is_done_callback
        self.view = BattleView()

        self.done()



