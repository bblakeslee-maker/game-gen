import dataclasses

from .chatbot import StoryTeller

@dataclasses.dataclass
class GameState:
    story_teller: StoryTeller
    window_size: tuple[int, int]
    is_prologue: bool
    battle_won: bool
