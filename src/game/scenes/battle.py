import arcade
from ..game_types import GameState
from ..entity import Entity
from textwrap import wrap as wrap_text
import random

PLAYER_SCALING = 1.0
BOSS_SCALING = 0.9

MENU_HEIGHT = 200

MAIN_ACTIONS = ["Attack", "Item", "Act"]
SUBACTIONS = {
    "Attack": ["Tackle", "Shoot", "Spit", "Embezzlement"],
    "Item": ["Big Hat", "Spurs", "Mysterious Orb"],
    "Act": ["Run", "Bribe", "Giddy Up"],
}
DESCRIPTIONS = {
    "Tackle": "The player tackles the enemy.",
    "Shoot": "The player shoots the enemy.",
    "Spit": "The player spits on the enemy.",
    "Embezzlement": "The player embezzles funds from the enemy.",
    "Big Hat": "A big hat. Very stylish!",
    "Spurs": "Spurs for a quick getaway.",
    "Mysterious Orb": "It's very mysterious.",
    "Run": "Run away from the battle.",
    "Bribe": "Try to bribe the enemy to go away.",
    "Giddy Up": "Command your horse to giddy up.",
}

class BattleView(arcade.View):
    def __init__(self, state, is_done_callback):
        super().__init__()
        self.done = is_done_callback
        self.time_elapsed = 0
        self.state = state
        self.width = state.window_size[0]
        self.height = state.window_size[1]
        self.battle_done = False
        self.current_main_action_index = 0  # Initial main action index is 0 (Attack)
        self.current_subaction_index = 0  # Initial subaction index is 0 (first action under Attack)
        self.current_panel = 0  # Initial panel is 0 (main actions panel)

    def on_show_view(self):
        self.background = arcade.load_texture(":resources:images/cybercity_background/far-buildings.png")
        # arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        self.clear()

        arcade.draw_lrwh_rectangle_textured(0, 0, self.width, self.height, self.background)

        player_image = self.state.image_generator.get_portrait('Bob')
        player_attacks = ["Tackle", "Shoot", "Spit", "Embezzlement"]

        self.player_char = Entity(player_image, player_attacks)

 
        self.player_sprite = arcade.Sprite(player_image, PLAYER_SCALING)
        self.player_sprite.center_x = 120
        self.player_sprite.center_y = 320
        self.player_sprite.draw()

        enemy_image = self.state.image_generator.get_portrait('Boss')
        self.enemy_sprite = arcade.Sprite(enemy_image, BOSS_SCALING)

        self.enemy_sprite.center_x = 620
        self.enemy_sprite.center_y = 420
        self.enemy_sprite.draw()

        BORDER_THICKNESS = 4  # border thickness in pixels
        for i in range(3):
            panel_x = self.width * (i * 2 + 1) / 6  # x position of the panel
            # Draw the border (larger rectangle)
            arcade.draw_rectangle_outline(panel_x, MENU_HEIGHT / 2, self.width / 3, MENU_HEIGHT, arcade.color.BLACK,
                                          BORDER_THICKNESS)
            # Draw the panel (smaller rectangle)
            arcade.draw_rectangle_filled(panel_x, MENU_HEIGHT / 2, self.width / 3 - BORDER_THICKNESS,
                                         MENU_HEIGHT - BORDER_THICKNESS, arcade.color.WHITE)

        # Draw the main action options
        for i, action in enumerate(MAIN_ACTIONS):
            color = arcade.color.BLACK if i == self.current_main_action_index else arcade.color.DIM_GRAY
            arcade.draw_text(action, self.width / 6 - 100, MENU_HEIGHT - (i + 1) * 30, color, font_size=20)

        # Draw the subaction options for the current main action
        for i, subaction in enumerate(SUBACTIONS[self.current_main_action]):
            color = arcade.color.BLACK if i == self.current_subaction_index else arcade.color.DIM_GRAY
            arcade.draw_text(subaction, self.width / 2 - 100, MENU_HEIGHT - (i + 1) * 30, color, font_size=21)

        # Draw the description for the current subaction
        if self.current_subaction in DESCRIPTIONS:
            description = DESCRIPTIONS.get(self.current_subaction, "")
            lines = wrap_text(description, 10)
            for i, line in enumerate(lines):
                y = MENU_HEIGHT / 2 + (len(lines) / 2 - i) * 25  # Dynamically adjust y position based on how many lines there are
                arcade.draw_text(line, self.width * 2 / 3 + 50, y, arcade.color.BLACK, font_size=20,
                                 width=self.width / 4, align="left")



    def on_key_press(self, key, modifiers):
        players_turn = True
        if players_turn:

            # If Up or Down arrow key is pressed
            if key in (arcade.key.UP, arcade.key.DOWN):
                if self.current_panel == 0:
                    if key == arcade.key.DOWN:
                        self.current_main_action_index += 1
                    else:
                        self.current_main_action_index -= 1
                # Wrap
                    self.current_main_action_index %= len(MAIN_ACTIONS)
                elif self.current_panel == 1:
                    if key == arcade.key.DOWN:
                        self.current_subaction_index += 1
                    else:
                        self.current_subaction_index -= 1
                    self.current_subaction_index %= len(SUBACTIONS[self.current_main_action])
            elif key == arcade.key.LEFT:
                if self.current_panel == 1:
                    self.current_panel -= 1
            elif key == arcade.key.RIGHT:
                if self.current_panel == 0:
                    self.current_panel += 1
            elif key in (arcade.key.SPACE, arcade.key.ENTER):
                if self.current_panel == 1:
                    print("Player attacks with: " + self.current_subaction)

    @property
    def current_main_action(self):
        return MAIN_ACTIONS[self.current_main_action_index]

    @property
    def current_subaction(self):
        return SUBACTIONS[self.current_main_action][self.current_subaction_index]

    def on_update(self, delta_time):
        self.time_elapsed += delta_time
        if self.time_elapsed > 2:
            battle_result = random.randint(0, 1)
            if(battle_result):
                self.state.battle_result = True
            print("state.battle_result: " + self.state.battle_result)
            self.battle_done = True
            self.done()



class BattleController:
    view: BattleView

    def __init__(self, state: GameState, is_done_callback):
        print("BattleController")
        self.done = is_done_callback
        self.view = BattleView(state, is_done_callback)
