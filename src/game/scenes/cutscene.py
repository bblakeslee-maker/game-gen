import arcade
from ..game_types import GameState

from game.background import Background

import game.dialog_box as dialog_box

class CutsceneEvent():
    def __init__(self, dialog, portrait, side, background):
        self.dialog = dialog
        self.portrait = portrait
        self.portrait_side = side
        self.background = background

class Portrait(arcade.Section):
    def __init__(self, left, bottom, width, height, **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)
        self.init_size = (width, height)
        self.background = None
        self.is_active = False
        self.is_open = False
        self.time_elapsed = 0


    def open(self, background):
        self.background = background
        self.is_open = True

    def close(self):
        self.background = None
        self.is_open = False

    def on_draw(self):
        if self.is_open:
            self.background.draw(self.left, self.bottom, self.width, self.height)

            if self.is_active:
                scalar = 1.2
            else:
                scalar = 1.

            self.width = self.init_size[0] * scalar
            self.height = self.init_size[1] * scalar


    def on_update(self, delta_time: float):
        self.time_elapsed += delta_time


class CutsceneView(arcade.View):
    def __init__(self, state: GameState, is_done_callback):
        super().__init__()
        self.state = state
        self.done = is_done_callback
        self.width = state.window_size[0]
        self.height = state.window_size[1]

        self.events = []
        self.index = 0

        self.dialog_height = 200
        self.portrait_width = 400
        self.portrait_height = 400
        self.portrait_side = 0

        # Add sections for each of the areas:
        self.bg_section = Background(0,
                                     self.dialog_height,
                                     self.width,
                                     self.height - self.dialog_height)
        if self.state.is_prologue:
            background_path = self.state.image_generator.get_background('prologue')
        else:
            if self.state.battle_won:
                background_path = self.state.image_generator.get_background('epilogue-victory')
            else:
                background_path = self.state.image_generator.get_background('epilogue-defeat')

        print(background_path)

        self.bg_section.open(dialog_box.Drawable(texture = arcade.load_texture(background_path)))

        self.dialog_section = dialog_box.DialogBox(0,
                                                   0,
                                                   self.width,
                                                   self.dialog_height)
        self.dialog_section.set_callback(lambda: self.dialog_next())
        # self.dialog_section.char_per_frame = -1

        self.left_char_portrait_section = Portrait(0,
                                                   self.dialog_section.height,
                                                   self.portrait_width,
                                                   self.portrait_height)

        self.right_char_portrait_section = Portrait(self.width - self.portrait_width,
                                                    self.dialog_section.height,
                                                    self.portrait_width,
                                                    self.portrait_height)

        self.section_manager.add_section(self.bg_section)
        self.section_manager.add_section(self.dialog_section)
        self.section_manager.add_section(self.left_char_portrait_section)
        self.section_manager.add_section(self.right_char_portrait_section)

        self.get_events_from_state()

    def get_events_from_state(self):
        dialog = ""

        if self.state.is_prologue:
            dialog = self.state.story_teller.prologue_dialogue
        else:
            if self.state.battle_won:
                dialog = self.state.story_teller.epilogue_victory_dialogue
            else:
                dialog = self.state.story_teller.epilogue_defeat_dialogue

        character_side = {}
        character_portrait = {}
        side = 0

        events = []

        lines = dialog.strip().split('\n')

        for line in lines:
            if line.find(': ') == -1:
                continue

            character, text = line.split(': ', 1)

            if character not in character_side:
                character_side[character] = side
                side = 1 - side

            if character not in character_portrait:
                char_name = self.state.story_teller.player_name if character_side[character] == 0 else self.state.story_teller.final_boss_name
                portrait_texture = self.state.image_generator.get_portrait(char_name)
                character_portrait[character] = arcade.load_texture(portrait_texture)

            events.append(CutsceneEvent(
                [line],
                dialog_box.Drawable(texture = character_portrait[character]),
                character_side[character],
                dialog_box.Drawable(color = arcade.color.GREEN)
            ))

        self.open(events)

    def dialog_next(self):
        self.dialog_section.next()
        if self.dialog_section.finished():
            self.next()

    def open(self, events):
        self.events = events
        self.index = 0

        if self.finished():
            self.state.is_prologue = False
            self.done()
            return

        event = self.events[self.index]
        self.trigger(event)

    def finished(self):
        return self.index == len(self.events)

    def next(self):
        self.index = min(self.index + 1, len(self.events))

        if self.finished():
            self.state.is_prologue = False
            self.done()
            return

        event = self.events[self.index]
        self.trigger(event)

    def trigger(self, event: CutsceneEvent):
        self.dialog_section.close()
        self.dialog_section.open(event.dialog)

        if event.portrait_side == 0:
            self.left_char_portrait_section.open(event.portrait)
        else:
            self.right_char_portrait_section.open(event.portrait)

        self.left_char_portrait_section.is_active = event.portrait_side == 0
        self.right_char_portrait_section.is_active = event.portrait_side == 1

    def on_update(self, delta_time: float):
        pass

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


class CutsceneController:
    view: CutsceneView

    def __init__(self, state: GameState, is_done_callback):
        print("CutsceneController")
        self.done = is_done_callback
        self.view = CutsceneView(state, is_done_callback)
