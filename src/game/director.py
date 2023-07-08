import arcade
from .scenes.battle import BattleController
from .scenes.cutscene import CutsceneController
from .scenes.setup import SetupController
from .game_types import GameState
from .chatbot import StoryTeller


class Director:
    state: GameState
    window: arcade.Window

    def __init__(self, window: arcade.Window):
        self.window = window
        self.state = GameState(story_teller=StoryTeller(use_chatgpt=False), window_size=(800, 600), is_prologue=True, battle_won=False)

        # Should be retrieved from the SetupController
        self.state.story_teller.add_basic_character_info("Bob", "Builder", "He can totally fix anything, except his marriage.")

        # game_flow = [SetupController, CutsceneController, BattleController, CutsceneController]
        game_flow = [SetupController, CutsceneController, BattleController, CutsceneController]
        self.scene_iter = iter(game_flow)
        self.current_scene = None

    def advance_game_flow(self):
        callback = self.advance_game_flow
        try:
            args = (self.state, callback)
            self.current_scene = next(self.scene_iter)(*args)
            self.window.show_view(self.current_scene.view)
        except StopIteration:
            print("Game Over!")
            self.window.close()
            arcade.exit()


    def start_game(self):
        self.advance_game_flow()
