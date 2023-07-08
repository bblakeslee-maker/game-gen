import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
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


class BattleScreen(arcade.View):
    def __init__(self):
        super().__init__()

    def on_show(self):
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Battle Simulation", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50, arcade.color.BLACK, font_size=50,
                         anchor_x="center")


class BattleMenu(arcade.View):
    def __init__(self):
        super().__init__()
        self.current_main_action_index = 0  # Initial main action index is 0 (Attack)
        self.current_subaction_index = 0  # Initial subaction index is 0 (first action under Attack)

        self.current_panel = 0  # Initial panel is 0 (main actions panel)

    def on_show(self):
        arcade.set_background_color(arcade.color.AIR_SUPERIORITY_BLUE)

    def on_draw(self):
        arcade.start_render()

        # Draw the panels
        arcade.draw_rectangle_filled(SCREEN_WIDTH / 4, MENU_HEIGHT / 2, SCREEN_WIDTH / 4, MENU_HEIGHT, arcade.color.WHITE)  # Main action panel
        arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, MENU_HEIGHT / 2, SCREEN_WIDTH / 4, MENU_HEIGHT, arcade.color.LIGHT_GRAY)  # Subaction panel
        arcade.draw_rectangle_filled(SCREEN_WIDTH * 3 / 4, MENU_HEIGHT / 2, SCREEN_WIDTH / 4, MENU_HEIGHT, arcade.color.GRAY)  # Description panel

        # Draw the main action options
        for i, action in enumerate(MAIN_ACTIONS):
            color = arcade.color.BLACK if action == self.current_main_action else arcade.color.DIM_GRAY
            arcade.draw_text(action, SCREEN_WIDTH / 4 - 100, MENU_HEIGHT - (i + 1) * 30, color, font_size=20, anchor_x="center")

        # Draw the subaction options for the current main action
        for i, subaction in enumerate(SUBACTIONS[self.current_main_action]):
            color = arcade.color.BLACK if subaction == self.current_subaction else arcade.color.DIM_GRAY
            arcade.draw_text(subaction, SCREEN_WIDTH / 2 - 100, MENU_HEIGHT - (i + 1) * 30, color, font_size=20, anchor_x="center")

        # Draw the description for the current subaction
        description = DESCRIPTIONS.get(self.current_subaction, "")
        arcade.draw_text(description, SCREEN_WIDTH * 3 / 4 - 100, MENU_HEIGHT / 2, arcade.color.BLACK, font_size=20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        # If Up or Down arrow key is pressed
        if key in (arcade.key.UP, arcade.key.DOWN):
            # Change the current action/subaction
            if self.current_panel == 0:  # Main actions
                self.current_main_action_index += 1 if key == arcade.key.DOWN else -1
                # Wrap around if out of bounds
                self.current_main_action_index %= len(MAIN_ACTIONS)
            elif self.current_panel == 1:  # Subactions
                self.current_subaction_index += 1 if key == arcade.key.DOWN else -1
                # Wrap around if out of bounds
                self.current_subaction_index %= len(SUBACTIONS[self.current_main_action_index])
        # If Left or Right arrow key is pressed
        elif key in (arcade.key.LEFT, arcade.key.RIGHT):
            # Change the current panel
            self.current_panel += 1 if key == arcade.key.RIGHT else -1
            # Wrap around if out of bounds
            self.current_panel %= 3  # 3 panels total

    @property
    def current_main_action(self):
        return MAIN_ACTIONS[self.current_main_action_index]

    @property
    def current_subaction(self):
        return SUBACTIONS[self.current_main_action][self.current_subaction_index]
