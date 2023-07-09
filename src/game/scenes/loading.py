import random
import arcade
from ..game_types import GameState

import game.dialog_box as dialog_box


TOOLTIPS = [
    "Somewhere out there, there's a server doing it's best just for you.",
    "Don't forget to breathe. Your character needs oxygen to survive.",
    "If you see an enemy, try attacking it. It might just work.",
    "Water is wet. Don't drown.",
    "If you're low on health, try using a healing item. It's like magic!",
    "Remember to save your game. You never know what might happen.",
    "If you're lost, try using a map. It's like having directions!",
    "Don't forget to equip weapons and armor. It might help you survive.",
    "If you're hungry, try eating food. Your character needs sustenance to function.",
    "If you're stuck, try talking to NPCs. They might have useful information.",
    "If you're tired, try resting. Your character needs sleep to regain energy.",
    "If you see a dragon, don't panic. Just remember to bring a lot of fire extinguishers.",
    "If you're feeling brave, try fighting a boss with your eyes closed. It's like playing on hard mode!",
    "If you're feeling lucky, try jumping off a cliff. Who knows, you might find a secret treasure at the bottom.",
    "If you're feeling lost, try asking the nearest NPC for directions. Just don't expect them to be helpful.",
    "If you're feeling bored, try talking to your party members. They might have some juicy gossip to share."
]


class LoadingView(arcade.View):
    def __init__(self, state: GameState, is_done_callback):
        super().__init__()
        self.state = state
        self.done = is_done_callback
        self.width = state.window_size[0]
        self.height = state.window_size[1]

        self.content = "Generating world..."
        self.content += "\n" * 10
        self.content += random.choice(TOOLTIPS)

        # Add sections for each of the areas:
        self.dialog_section = dialog_box.DialogBox(0,
                                                   0,
                                                   self.width,
                                                   self.height)
        self.dialog_section.set_callback(lambda: self.dialog_next())
        self.dialog_section.char_per_frame = -1

        self.section_manager.add_section(self.dialog_section)

        self.dialog_section.open([self.content])
        self.time_elapsed = 0

    def dialog_next(self):
        self.dialog_section.next()
        if self.dialog_section.finished():
            self.dialog_section.close()


    def on_update(self, delta_time: float):
        self.time_elapsed += delta_time
        if self.time_elapsed > 2.:
            self.done()


    def on_draw(self):
        arcade.start_render()

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, _buttons: int, _modifiers: int):
        pass

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.dialog_next()

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        pass

    def on_mouse_enter(self, x: float, y: float):
        pass

    def on_mouse_leave(self, x: float, y: float):
        pass



class LoadingController:
    view: LoadingView

    def __init__(self, state: GameState, is_done_callback):
        print("LoadingController")
        self.done = is_done_callback
        self.view = LoadingView(state, is_done_callback)
