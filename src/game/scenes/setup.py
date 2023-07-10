import arcade
import arcade.gui
from ..game_types import GameState


QUESTIONS = [
    "Character Name:",
    "Character Occupation:",
    "Any Additional Info:"
]

ENABLE_DEFAULT_ANSWERS = False
DEFAULT_ANSWERS = [
    "Angus McFife",
    "Fighter, Protector of Dundee",
    "Angus uses is mighty hammer to protect the land of Fife. His enemy is Zargothrax: Master of Nightmares, Keeper of Celestial Flame, Sorcerer, Bound to the Darkness, Wizard King, Chaos Incarnate"
]

class SetupView(arcade.View):
    def __init__(self, state: GameState, is_done_callback):
        super().__init__()
        self.state = state
        self.done = is_done_callback
        self.time_elapsed = 0

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Set background color
        arcade.set_background_color((10,10,10))
        self.v_box = arcade.gui.UIBoxLayout()
        self.question_iter = zip(QUESTIONS, DEFAULT_ANSWERS)
        self.question_widget = None

        # # Create a text label
        question, answer = next(self.question_iter)
        self.question_label = arcade.gui.UITextArea(
                                            text=question,
                                            width=600,
                                            height=40,
                                            font_size=24,
                                            font_name="Arial")
        self.v_box.add(self.question_label)

        # Create an entry box
        text = ""
        if ENABLE_DEFAULT_ANSWERS:
            text = answer
        self.text_area = arcade.gui.UIInputText(text=text,
                                           width=700,
                                           height=200,
                                           font_size=16,
                                           font_name="Arial",
                                           multiline=True)

        bg_tex = arcade.load_texture(":resources:gui_basic_assets/window/grey_panel.png")
        self.v_box.add(
            arcade.gui.UITexturePane(
                self.text_area.with_space_around(left=20),
                tex=bg_tex,
                padding=(20, 20, 20, 20)
            )
        )


        # # Create a UITextureButton
        texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/play.png")
        ui_texture_button = arcade.gui.UITextureButton(texture=texture)

        # # Handle Clicks
        @ui_texture_button.event("on_click")
        def on_click_texture_button(event):

            self.state.setup_results[self.question_label.text] = self.text_area.text
            try:
                question, answer = next(self.question_iter)
                self.question_label.text = question
                self.text_area.text = "" if not ENABLE_DEFAULT_ANSWERS else answer
            except StopIteration:
                print(self.state.setup_results)
                self.manager.clear()
                self.done()


        #
        self.v_box.add(ui_texture_button.with_space_around(top=20))
        #
        # # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box
            )
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()


class SetupController:
    view: SetupView

    def __init__(self, state: GameState, is_done_callback):
        print("SetupController")
        self.done = is_done_callback
        self.view = SetupView(state, is_done_callback)
