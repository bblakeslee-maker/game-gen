import arcade
from ..game_types import GameState
from ..entity import Entity
from textwrap import wrap as wrap_text
import random
import json

PLAYER_SCALING = 0.8
BOSS_SCALING = 0.8

MENU_HEIGHT = 200

BOSS_MAX_HP = 500
PLAYER_MAX_HP = 1000


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
        self.post_action_phase = False
        self.post_action_text = "If you see this something has happened out of order"
        self.time_in_post_action = 0.0
        self.battle_done = False
        self.current_main_action_index = 0  # Initial main action index is 0 (Attack)
        self.current_subaction_index = 0  # Initial subaction index is 0 (first action under Attack)
        self.current_panel = 0  # Initial panel is 0 (main actions panel)
        self.players_turn = True
        self.boss_health = BOSS_MAX_HP
        self.player_health = PLAYER_MAX_HP
        self.boss_items_left = 2
        # self.boss_final_wind_flag = False
        self.player_attacks = self.state.story_teller.main_character_attacks
        self.player_items = self.state.story_teller.main_character_inventory
        self.enemy_attacks = self.state.story_teller.final_boss_attacks
        self.enemy_items = self.state.story_teller.final_boss_inventory
        self.main_actions = ["Attack", "Item"]
        self.subactions = {
            "Attack": [x["name"] for x in self.player_attacks],
            "Item": [x["name"] for x in self.player_items]
        }
        self.actions_descriptions = {
            x["name"]: x["description"] for x in self.player_attacks + self.player_items
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
        self.player_sprite.center_x = self.width / 6
        self.player_sprite.center_y = 440
        self.player_sprite.draw()

        enemy_image = self.state.image_generator.get_portrait(self.state.story_teller.final_boss_name)
        self.enemy_sprite = arcade.Sprite(enemy_image, BOSS_SCALING)

        self.enemy_sprite.center_x = (self.width / 2) + (self.width / 3) 
        self.enemy_sprite.center_y = 500
        self.enemy_sprite.draw()

        self.player_hp_bar.draw()
        self.enemy_hp_bar.draw()

        BORDER_THICKNESS = 4  # border thickness in pixels
        
        if self.post_action_phase == True:
            arcade.draw_rectangle_filled(self.width / 2, MENU_HEIGHT / 2, self.width, MENU_HEIGHT, arcade.color.BLACK, 0)
            # arcade.draw_text(self.post_action_text, self.width / 2, self.height / 2, arcade.color.WHITE, font_size=32, align="center")
            arcade.draw_text(self.post_action_text, 0, MENU_HEIGHT / 2, arcade.color.WHITE, font_size=20, width=self.width, align="center")
        else:
            for i in range(3):
                panel_x = self.width * (i * 2 + 1) / 6  # x position of the panel
                # Draw the border (larger rectangle)
                arcade.draw_rectangle_outline(panel_x, MENU_HEIGHT / 2, self.width / 3, MENU_HEIGHT, arcade.color.BLACK,
                                            BORDER_THICKNESS)
                if self.current_panel == 0 and i != 0:
                    panel_color = arcade.color.DIM_GRAY
                elif self.current_panel == 1 and i == 0:
                    panel_color = arcade.color.DIM_GRAY
                else:
                    panel_color = arcade.color.WHITE

                # Draw the panel (smaller rectangle)
                arcade.draw_rectangle_filled(panel_x, MENU_HEIGHT / 2, self.width / 3 - BORDER_THICKNESS,
                                            MENU_HEIGHT - BORDER_THICKNESS, panel_color)


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
                action_effect_text = ""
                accuracy_text = ""

                action_effect = 0
                if self.current_main_action_index == 0:
                    action_effect = int(self.player_attacks[self.current_subaction_index]["damage"])
                    action_accuracy = str(self.player_attacks[self.current_subaction_index]["accuracy"])
                    accuracy_text += "Accuracy: " + action_accuracy + "%"
                elif self.current_main_action_index == 1:
                    action_effect = int(self.player_items[self.current_subaction_index]["damage"])

                if action_effect == 0:
                    action_effect_text += "has no effect..."
                elif action_effect > 0:
                    action_effect_text += "Deals: " + str(action_effect) +  " Damage"
                else:
                    action_effect_text += "Heals: " + str(abs(action_effect)) +  "HP"

                lines = wrap_text(description, 32)
                last_y = 0
                for i, line in enumerate(lines):
                    y = MENU_HEIGHT / 2 + (len(lines) / 2 - i) * 25  # Dynamically adjust y position based on how many lines there are
                    arcade.draw_text(line, self.width * 2 / 3 + 50, y, arcade.color.BLACK, font_size=16,
                                    width=self.width / 4, align="left")
                    last_y = y
                
          
                arcade.draw_text(action_effect_text, self.width * 2 / 3 + 50, last_y - 30, arcade.color.BLACK, font_size=16, 
                                    width=self.width / 4, align="left")

                arcade.draw_text(accuracy_text, self.width * 2 / 3 + 50, last_y - 55, arcade.color.BLACK, font_size=16, 
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
                    self.current_subaction_index %= len(self.subactions[self.current_main_action])
                elif self.current_panel == 1:
                    if key == arcade.key.DOWN:
                        self.current_subaction_index += 1
                    else:
                        self.current_subaction_index -= 1
                    self.current_subaction_index %= len(self.subactions[self.current_main_action])

            elif key == arcade.key.LEFT:
                if self.current_panel == 1:
                    self.current_panel -= 1
                    self.current_subaction_index %= len(self.subactions[self.current_main_action])
            elif key == arcade.key.RIGHT:
                if self.current_panel == 0:
                    self.current_panel += 1
                    self.current_subaction_index %= len(self.subactions[self.current_main_action])
            elif key in (arcade.key.SPACE, arcade.key.ENTER):
                if self.current_panel == 1:
                    if self.current_main_action_index == 0:
                        damage = int(self.player_attacks[self.current_subaction_index]["damage"])

                        if isinstance(self.player_attacks[self.current_subaction_index]["accuracy"], str):
                            accuracy = int(self.player_attacks[self.current_subaction_index]["accuracy"].rstrip('%'))
                        else:
                            accuracy = int(self.player_attacks[self.current_subaction_index]["accuracy"])

                        if random.randrange(100) < accuracy:
                            if damage >= 0:
                                player_action_text = "Attack hit for " + str(damage) + " damage"
                            else:
                                player_action_text = "Player healed " + str(abs(damage)) + " HP"
                        else:
                            damage = 0
                            player_action_text = "Player's attack missed..."

                    elif self.current_main_action_index == 1:
                        damage = int(self.player_items[self.current_subaction_index]["damage"])
                        player_action_text = "Player used item " + self.player_items[self.current_subaction_index]["name"]

                    self.post_action_text = player_action_text
                    print(player_action_text)
                    self.post_action_phase = True

                    if damage >= 0:
                        # Final stand mechanic that's not really working
                        # if -200 < (self.boss_health - damage) < 0 and self.boss_final_wind_flag == False:
                        #     self.boss_health = 400
                        #     boss_final_wind_flag = True
                        #     print("Final blow wasn't strong enough boss experiances final wind")
                        # else:
                        #     self.boss_health -= damage
                        self.boss_health -= damage
                    else:
                        self.player_health -= damage

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
            self.post_action_text = "You have vanquished " + self.state.story_teller.final_boss_name

        if self.post_action_phase == True:
            self.time_in_post_action += delta_time
            if self.time_in_post_action > 1.5:
                self.time_in_post_action = 0
                self.post_action_phase = False
                if self.battle_done:
                    self.done()

        else:
            # Boss's Turn
            if self.players_turn == False:

                boss_action_text = ""
                    
                if self.enemy_items and self.boss_items_left > 0 and random.randrange(100) < 30: # Should boss use item
                     # Randomly pick an item
                    enemy_item = random.choice(self.enemy_items)
                    item_name = enemy_item["name"]
                    damage = int(enemy_item["damage"])
                    if damage > 0:
                        self.player_health -= damage
                        boss_action_text = self.state.story_teller.final_boss_name + " attacks with item " + item_name + " for " + str(damage) + " damage"
                    else:
                        self.boss_health -= damage
                        boss_action_text = self.state.story_teller.final_boss_name + " heals with item " + item_name + " for " + str(abs(damage)) + " HP"
                    self.boss_items_left -= 1
                elif self.enemy_attacks:
                    # Randomly pick an attack
                    enemy_attack = random.choice(self.enemy_attacks)
                    print("enemy attack", enemy_attack)
                    attack_name = enemy_attack["name"]
                    damage = int(enemy_attack["damage"])
                    if isinstance(enemy_attack["accuracy"], str):
                        accuracy = int(enemy_attack["accuracy"].rstrip('%'))
                    else:
                        accuracy = int(enemy_attack["accuracy"])

                        if random.randrange(100) < accuracy:
                            if damage > 0:
                                self.player_health -= damage
                                boss_action_text = self.state.story_teller.final_boss_name + " attacks with " + attack_name + " for " + str(damage) + " damage"
                            else:
                                self.boss_health -= damage
                                boss_action_text = self.state.story_teller.final_boss_name + " heals with " + attack_name + " for " + str(abs(damage)) + "HP"
                        else:
                            damage = 0
                            boss_action_text = self.state.story_teller.final_boss_name + "'s attack missed..."

                    # if damage > 0:
                    #     self.player_health -= damage
                    #     boss_action_text = self.state.story_teller.final_boss_name + " attacks with " + attack_name + " for " + str(damage) + " damage"
                    # else:
                    #     self.boss_health -= damage
                    #     boss_action_text = self.state.story_teller.final_boss_name + " heals with " + attack_name + " for " + str(abs(damage)) + "HP"

                print(boss_action_text)

                self.post_action_phase = True
                self.post_action_text = boss_action_text
                self.players_turn = True

        if self.player_health <= 0:
            self.state.battle_won = False
            self.battle_done = True
            self.post_action_text = "YOU HAVE BEEN DEFEATED"




class BattleController:
    view: BattleView

    def __init__(self, state: GameState, is_done_callback):
        print("BattleController")
        self.done = is_done_callback
        self.view = BattleView(state, is_done_callback)
