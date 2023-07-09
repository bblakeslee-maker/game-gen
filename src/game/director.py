import arcade
import concurrent.futures
from pathlib import Path

from .scenes.battle import BattleController
from .scenes.cutscene import CutsceneController
from .scenes.setup import SetupController
from .scenes.text_dump import TextDumpController
from .scenes.loading import LoadingController
from .scenes.title import TitleController
from .game_types import GameState
from .chatbot import StoryTeller
from .stable_diffusion import ImageGenerator
from .audio_player import AudioManager

MUSIC_DIR = Path(__file__).parent / 'music'
MUSIC_VOL = 0.5

class Director:
    state: GameState
    window: arcade.Window

    def __init__(self, window: arcade.Window):
        self.window = window

        self.state = GameState(
            story_teller=StoryTeller(use_chatgpt=True),
            window_size=window.size,
            is_prologue=True,
            battle_won=False,
            image_generator=ImageGenerator(),
            audio_manager=AudioManager(music_dir=MUSIC_DIR))

        game_flow = [SetupController, LoadingController, TitleController, TextDumpController, LoadingController, CutsceneController, BattleController, CutsceneController]
        self.scene_iter = iter(game_flow)
        self.current_scene = None
        self.stage_count = 0
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    def advance_game_flow(self):

        self.stage_count += 1
        if self.stage_count == 3:
            # Use the results from the first scene to set up the story teller

            print("Generating story.....")
            # Should be retrieved from the SetupController
            name, occupation, more_info = self.state.setup_results.values()
            self.state.story_teller.add_basic_character_info(name, occupation, more_info)

            # Generate story

            print("select_story_genre")
            self.state.story_teller.select_story_genre()
            print("select_artistic_tone")
            self.state.story_teller.select_artistic_tone()
            print("create_prologue")
            self.state.story_teller.create_prologue()
            print("create_title")
            self.state.story_teller.create_title()

            self.state.story_teller.create_title_card_prompt()

            print('create_background title card')
            title_prompt = self.state.story_teller.title_card_prompt
            self.state.image_generator.create_background('title-card', title_prompt)

            def content_in_the_background():
                print("create_main_character")
                self.state.story_teller.create_main_character()
                print("create_final_boss")
                self.state.story_teller.create_final_boss()
                print("create_prologue_dialogue")
                self.state.story_teller.create_prologue_dialogue()

                # TODO: move to end content
                print("create_endings")
                self.state.story_teller.create_endings()
                print("create_epilogue_dialogue")
                self.state.story_teller.create_epilogue_dialogue()
                print("create_story_card_prompts")
                self.state.story_teller.create_story_card_prompts()

                print("Generating images....")
                print('create_character hero')
                character_prompt = self.state.story_teller.main_character_prompt
                self.state.image_generator.create_character(name, character_prompt, no_bg=True)

                print('create_character boss')
                character_prompt = self.state.story_teller.final_boss_prompt
                self.state.image_generator.create_character(self.state.story_teller.final_boss_name, character_prompt, no_bg=True)

                print('create_background prologue')
                prologue_prompt = self.state.story_teller.prologue_card_prompt
                self.state.image_generator.create_background('prologue', prologue_prompt)

                # TODO: move to end content
                print('create_background epilogue-victory')
                epilogue_victory_prompt = self.state.story_teller.epilogue_victory_card_prompt
                self.state.image_generator.create_background('epilogue-victory', epilogue_victory_prompt)

                print('create_background epilogue-defeat')
                epilogue_defeat_prompt = self.state.story_teller.epilogue_defeat_card_prompt
                self.state.image_generator.create_background('epilogue-defeat', epilogue_defeat_prompt)

            self.state.story_generation_future = self.executor.submit(content_in_the_background)


            def final_content_in_background():
                pass
                # print("create_endings")
                # self.state.story_teller.create_endings()
                # print("create_epilogue_dialogue")
                # self.state.story_teller.create_epilogue_dialogue()
                # print("create_story_card_prompts")
                # self.state.story_teller.create_story_card_prompts()
                #
                # epilogue_victory_prompt = self.state.story_teller.epilogue_victory_card_prompt
                # self.state.image_generator.create_background('epilogue-victory', epilogue_victory_prompt)
                #
                # epilogue_defeat_prompt = self.state.story_teller.epilogue_defeat_card_prompt
                # self.state.image_generator.create_background('epilogue-defeat', epilogue_defeat_prompt)

            self.state.ending_content_future = self.executor.submit(final_content_in_background)

        if self.stage_count == 3:
            # play intro music
            music_file = self.state.audio_manager.get_intro_music()
            audio = arcade.load_sound(str(music_file),True)
            self.state.audio_player = arcade.play_sound(audio, MUSIC_VOL, looping=True)
        elif self.stage_count == 7:
            # play battle music
            arcade.stop_sound(self.state.audio_player)

            music_file = self.state.audio_manager.get_battle_music()
            audio = arcade.load_sound(str(music_file),True)
            self.state.audio_player = arcade.play_sound(audio,MUSIC_VOL, looping=True)
        elif self.stage_count == 8:
            if self.state.battle_won:
                # play victory music
                arcade.stop_sound(self.state.audio_player)

                music_file = self.state.audio_manager.get_victory_music()
                audio = arcade.load_sound(str(music_file),True)
                self.state.audio_player = arcade.play_sound(audio,MUSIC_VOL, looping=True)
            else:
                # play defeat music
                arcade.stop_sound(self.state.audio_player)

                music_file = self.state.audio_manager.get_defeat_music()
                audio = arcade.load_sound(str(music_file),True)
                self.state.audio_player = arcade.play_sound(audio,MUSIC_VOL, looping=True)

        if self.stage_count > 5:
            # Wait for the story and images to generate
            self.state.story_generation_future.result()

        if self.stage_count > 7:
            # Wait for the final content to generate
            self.state.ending_content_future.result()

        callback = self.advance_game_flow
        try:
            args = (self.state, callback)
            self.current_scene = next(self.scene_iter)(*args)
            self.window.clear()
            self.window.show_view(self.current_scene.view)
        except StopIteration:
            print("Game Over!")
            self.window.close()
            arcade.exit()


    def start_game(self):
        self.advance_game_flow()
