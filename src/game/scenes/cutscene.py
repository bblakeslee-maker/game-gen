import arcade

class CutsceneView(arcade.View):
    ...


class CutsceneController:
    view: CutsceneView

    def __init__(self, is_done_callback):
        print("CutsceneController")
        self.done = is_done_callback
        self.view = CutsceneView()

        self.done()
