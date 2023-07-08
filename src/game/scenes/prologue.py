import arcade

class PrologueView(arcade.View):
    ...


class PrologueController:
    view: PrologueView

    def __init__(self, is_done_callback):
        super().__init__(is_done_callback)

