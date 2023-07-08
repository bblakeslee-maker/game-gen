import arcade
from scenes.battle import BattleController
from scenes.cutscene import CutsceneController
from scenes.prologue import PrologueController



class Director:
    def __init__(self, window: arcade.Window):
        self.window = window

        game_flow = [PrologueController, CutsceneController, BattleController, CutsceneController]
        self.scene_iter = iter(game_flow)
        self.current_scene = None


    def advance_game_flow(self):
        callback = self.advance_game_flow
        try:
            self.current_scene = next(self.scene_iter)(callback)
        except StopIteration:
            print("Game Over!")
            # Stop the game


    def start_game(self):
        self.advance_game_flow()
        self.window.show_view(self.current_scene.view)

