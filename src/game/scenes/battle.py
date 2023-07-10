import arcade
from ..game_types import GameState
from ..entity import Entity
from textwrap import wrap as wrap_text
import random
import json

PLAYER_SCALING = 1.0
BOSS_SCALING = 0.9

MENU_HEIGHT = 200

BOSS_MAX_HP = 2600
PLAYER_MAX_HP = 2400


class HPStatusBar:
    def __init__(self, max_hp, current_hp, x, y, width, height, background_color, foreground_color, border_color):
        self.max_hp = max_hp
        self.current_hp = current_hp
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.background_color = background_color
        self.foreground_color = foreground_color
        self.border_color = border_color

    def draw(self):

        margin = 4
        # Draw the background
        arcade.draw_xywh_rectangle_filled(self.x-margin, self.y-margin, self.width+margin*2, self.height+margin*2, self.border_color)
        arcade.draw_xywh_rectangle_filled(self.x, self.y, self.width, self.height, self.background_color)

        # Calculate the width of the foreground based on the current HP
        foreground_width = (self.current_hp / self.max_hp) * self.width

        # Draw the foreground
        arcade.draw_xywh_rectangle_filled(self.x, self.y, foreground_width, self.height, self.foreground_color)

    def update(self, current_hp):
        self.current_hp = current_hp

class BattleView(arcade.View):
    def __init__(self, state, is_done_callback):
        super().__init__()
        self.done = is_done_callback
        self.time_elapsed = 0
        self.state:GameState = state
        self.width = state.window_size[0]
        self.height = state.window_size[1]
        self.battle_done = False
        self.current_main_action_index = 0  # Initial main action index is 0 (Attack)
        self.current_subaction_index = 0  # Initial subaction index is 0 (first action under Attack)
        self.current_panel = 0  # Initial panel is 0 (main actions panel)
        self.players_turn = True
        self.boss_health = BOSS_MAX_HP
        self.player_health = PLAYER_MAX_HP
        self.boss_final_wind_flag = False
        self.player_attacks = json.loads(self.state.story_teller.main_character_attacks)
        self.player_items = json.loads(self.state.story_teller.main_character_inventory)
        self.enemy_attacks = json.loads(self.state.story_teller.final_boss_attacks)
        self.enemy_items = json.loads(self.state.story_teller.final_boss_inventory)
        self.main_actions = ["Attack", "Item"]
        self.subactions = {
            "Attack": [self.player_attacks[0]["name"], self.player_attacks[1]["name"], self.player_attacks[2]["name"], self.player_attacks[3]["name"]],
            "Item": [self.player_items[0]["name"], self.player_items[1]["name"]],
            # "Act": ["Run", "Bribe", "Giddy Up"],
        }
        self.actions_descriptions = {
            self.player_attacks[0]["name"]: self.player_attacks[0]["description"],
            self.player_attacks[1]["name"]: self.player_attacks[1]["description"],
            self.player_attacks[2]["name"]: self.player_attacks[2]["description"],
            self.player_attacks[3]["name"]: self.player_attacks[3]["description"],
            self.player_items[0]["name"]: self.player_items[0]["description"],
            self.player_items[1]["name"]: self.player_items[1]["description"],

            # "Run": "Run away from the battle.",
        }

        self.player_hp_bar = HPStatusBar(
            PLAYER_MAX_HP, self.player_health,
            0, 200,
            400, 20,
            arcade.color.DARK_GRAY, arcade.color.RED, arcade.color.BLACK)
        self.enemy_hp_bar = HPStatusBar(
            BOSS_MAX_HP, self.boss_health,
            self.width-400, 200,
            400, 20,
            arcade.color.DARK_GRAY, arcade.color.RED, arcade.color.BLACK)

    def on_show_view(self):
        background_path = self.state.image_generator.get_background('battle')
        self.background = arcade.load_texture(background_path)


    def on_draw(self):
        self.clear()


        player_image = self.state.image_generator.get_portrait(self.state.story_teller.player_name, look_right=True)
        arcade.draw_lrwh_rectangle_textured(0, 0, self.width, self.height, self.background)

        self.player_sprite = arcade.Sprite(player_image, PLAYER_SCALING)
        self.player_sprite.center_x = 120
        self.player_sprite.center_y = 320
        self.player_sprite.draw()

        enemy_image = self.state.image_generator.get_portrait(self.state.story_teller.final_boss_name)
        self.enemy_sprite = arcade.Sprite(enemy_image, BOSS_SCALING)

        self.enemy_sprite.center_x = 750
        self.enemy_sprite.center_y = 420
        self.enemy_sprite.draw()

        self.player_hp_bar.draw()
        self.enemy_hp_bar.draw()

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
        for i, action in enumerate(self.main_actions):
            color = arcade.color.BLACK if i == self.current_main_action_index else arcade.color.DIM_GRAY
            arcade.draw_text(action, self.width / 6 - 100, MENU_HEIGHT - (i + 1) * 30, color, font_size=20)

        # Draw the subaction options for the current main action
        for i, subaction in enumerate(self.subactions[self.current_main_action]):
            color = arcade.color.BLACK if i == self.current_subaction_index else arcade.color.DIM_GRAY
            arcade.draw_text(subaction, self.width / 2 - 100, MENU_HEIGHT - (i + 1) * 30, color, font_size=21)

        # Draw the description for the current subaction
        if self.current_subaction in self.actions_descriptions:
            description = self.actions_descriptions.get(self.current_subaction, "")
            lines = wrap_text(description, 10)
            for i, line in enumerate(lines):
                y = MENU_HEIGHT / 2 + (len(lines) / 2 - i) * 25  # Dynamically adjust y position based on how many lines there are
                arcade.draw_text(line, self.width * 2 / 3 + 50, y, arcade.color.BLACK, font_size=20,
                                 width=self.width / 4, align="left")



    def on_key_press(self, key, modifiers):
        if self.players_turn:
            # If Up or Down arrow key is pressed
            if key in (arcade.key.UP, arcade.key.DOWN):
                if self.current_panel == 0:
                    if key == arcade.key.DOWN:
                        self.current_main_action_index += 1
                    else:
                        self.current_main_action_index -= 1
                    # Wrap
                    self.current_main_action_index %= len(self.main_actions)
                elif self.current_panel == 1:
                    if key == arcade.key.DOWN:
                        self.current_subaction_index += 1
                    else:
                        self.current_subaction_index -= 1
                    self.current_subaction_index %= len(self.subactions[self.current_main_action])

            elif key == arcade.key.LEFT:
                if self.current_panel == 1:
                    self.current_panel -= 1
            elif key == arcade.key.RIGHT:
                if self.current_panel == 0:
                    self.current_panel += 1
            elif key in (arcade.key.SPACE, arcade.key.ENTER):
                if self.current_panel == 1:
                    damage = int(self.player_attacks[self.current_subaction_index]["damage"])
                    print("Player attacks with: " + self.current_subaction + " for " + str(damage) + " damage")

                    if -200 < (self.boss_health - damage) < 0 and self.boss_final_wind_flag == False:
                        self.boss_health = 400
                        boss_final_wind_flag = True
                        print("Final blow wasn't strong enough boss experiances final wind")
                    else:
                        self.boss_health -= damage

                    print("Boss health is currently " + str(self.boss_health))
                    self.players_turn = False


    @property
    def current_main_action(self):
        return self.main_actions[self.current_main_action_index]

    @property
    def current_subaction(self):
        return self.subactions[self.current_main_action][self.current_subaction_index]

    def on_update(self, delta_time):

        self.player_hp_bar.update(self.player_health)
        self.enemy_hp_bar.update(self.boss_health)

        if self.boss_health <= 0:
            self.state.battle_won = True
            self.battle_done = True
            self.done()
        

        # Boss's Turn
        if self.players_turn == False:

            # Randomly pick an action
            enemy_attack_index = random.randint(0, 3)

            attack_name = self.enemy_attacks[enemy_attack_index]["name"]
            damage = int(self.enemy_attacks[enemy_attack_index]["damage"])
            self.player_health -= damage

            print("boss attacks with: " + attack_name + " for " + str(damage) + " damage")

            # If health is less than 50% have a chance to use a healing attack if slot is left

            # If health is less than 25% have a chance to use a healing item if not used up

            # Else Pick a random attack

            self.players_turn = True


        if self.player_health <= 0:
            self.state.battle_won = False
            self.battle_done = True
            self.done()



class BattleController:
    view: BattleView

    def __init__(self, state: GameState, is_done_callback):
        print("BattleController")
        self.done = is_done_callback
        self.view = BattleView(state, is_done_callback)
