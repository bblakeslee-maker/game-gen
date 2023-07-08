import arcade

class CutsceneView(arcade.View):
    ...


class CutsceneController:
    view: CutsceneView

    def __init__(self, is_done_callback):
        super().__init__(is_done_callback)

