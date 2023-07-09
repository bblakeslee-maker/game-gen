import arcade

class Entity(arcade.Sprite):
    def __init__(self, sprite_file, attacks):
        super().__init__()

        self.texture = arcade.load_texture(sprite_file, flipped_horizontally=True)

        self.health = 50
        self.MAIN_ACTIONS = ["Attack", "Item", "Act"]
        self.attacks = attacks
        self.items = []
        self.acts = []

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