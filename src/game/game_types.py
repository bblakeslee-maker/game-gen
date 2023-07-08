import dataclasses

from .chatbot import StoryTeller
from .stable_diffusion import ImageGenerator

@dataclasses.dataclass
class GameState:
    story_teller: StoryTeller
    image_generator: ImageGenerator