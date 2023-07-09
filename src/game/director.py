import arcade
from .scenes.battle import BattleController
from .scenes.cutscene import CutsceneController
from .scenes.setup import SetupController
from .scenes.text_dump import TextDumpController
from .game_types import GameState
from .chatbot import StoryTeller
from .stable_diffusion import ImageGenerator

class Director:
    state: GameState
    window: arcade.Window

    def __init__(self, window: arcade.Window):
        self.window = window
        self.state = GameState(
            story_teller=StoryTeller(use_chatgpt=False),
            window_size=window.size,
            is_prologue=True,
            battle_won=False,
            image_generator=ImageGenerator())

        game_flow = [SetupController, TextDumpController, CutsceneController, BattleController, CutsceneController]
        self.scene_iter = iter(game_flow)
        self.current_scene = None
        self.stage_count = 0


    def advance_game_flow(self):

        self.stage_count += 1
        if self.stage_count == 2:
            # Use the results from the first scene to set up the story teller

            print("Generating story.....")

            # Should be retrieved from the SetupController
            name, occupation, more_info = self.state.setup_results.values()
            self.state.story_teller.add_basic_character_info(name, occupation, more_info)

            # Generate story
            self.state.story_teller.generate_story()

            print("Generating images....")
            # Create main character image
            character_prompt = self.state.story_teller.main_character_prompt
            self.state.image_generator.create_character('Bob', character_prompt)

            # Create boss image
            character_prompt = self.state.story_teller.final_boss_prompt
            self.state.image_generator.create_character('Boss', character_prompt)

            print('Generating prologue card....')
            prologue_prompt = self.state.story_teller.prologue_card_prompt
            self.state.image_generator.create_background('prologue', prologue_prompt)


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
