from pathlib import Path
import random
import json

class AudioManager:
    def __init__(self, music_dir:Path):
        self.music_dir = music_dir

        with (music_dir / 'index.json').open() as f:
            music_index = json.load(f)

        self.music_index = music_index

    def pick_audio_file(self, type:str):
        file_name = self.music_dir / random.choice(self.music_index[type])
        return file_name

    def get_intro_music(self):
        return self.pick_audio_file('intro')

    def get_battle_music(self):
        return self.pick_audio_file('battle')

    def get_victory_music(self):
        return self.pick_audio_file('victory')

    def get_defeat_music(self):
        return self.pick_audio_file('defeat')