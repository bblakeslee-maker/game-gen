import dataclasses

from .chatbot import StoryTeller
from .stable_diffusion import ImageGenerator

@dataclasses.dataclass
class GameState:
    story_teller: StoryTeller
    image_generator: ImageGenerator
    window_size: tuple[int, int]
    is_prologue: bool
    battle_won: bool
