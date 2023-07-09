import arcade

class MouseSection(arcade.Section):
    def __init__(self, left, bottom, width, height, **kwargs):
        super().__init__(left, bottom, width, height)
        self.kwargs = kwargs

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if 'on_mouse_press' in self.kwargs:
            self.kwargs['on_mouse_press']()
