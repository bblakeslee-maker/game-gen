import arcade


class BattleView(arcade.View):
    ...


class BattleController:
    view: BattleView

    def __init__(self, is_done_callback):
        super().__init__(is_done_callback)



