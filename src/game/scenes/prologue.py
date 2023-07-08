import arcade

class PrologueView(arcade.View):
    ...


class PrologueController:
    view: PrologueView

    def __init__(self, is_done_callback):
        print("PrologueController")
        self.done = is_done_callback
        self.view = PrologueView()

        self.done()

