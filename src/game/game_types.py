import dataclasses
from concurrent.futures import Future

from .chatbot import StoryTeller
from .stable_diffusion import ImageGenerator

@dataclasses.dataclass
class GameState:
    story_teller: StoryTeller
    image_generator: ImageGenerator
    window_size: tuple[int, int]
    is_prologue: bool
    battle_won: bool
    story_generation_future: Future | None = None
    ending_content_future: Future | None = None
    setup_results: dict[str, str] = dataclasses.field(default_factory=dict)
