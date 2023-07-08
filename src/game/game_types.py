import dataclasses

from .chatbot import StoryTeller

@dataclasses.dataclass
class GameState:
    story_teller: StoryTeller
