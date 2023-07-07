'''
1) Create interface for GPT prompt
2) Create a T pose character profile
3) Control character pose with control net, through automatic
4) Create character class to store the "likeness" of a character
    - Store the character description, negative prompts, T pose (front and back), and attack types
'''
import numpy as np
from typing import List, Dict

class Character:
    descriptors: List[str]
    front_pose: np.ndarray
    back_pose: np.ndarray
    negative_prompts: List[str]
    attack_types: Dict[str, np.ndarray]

    def __init__(
        self,
        descriptors,
        front_pose,
        back_pose,
        negative_prompts,
        attack_types,
        attack_sprites,
    ):

        self.descriptors = descriptors
        self.front_pose = front_pose
        self.back_pose = back_pose
        self.negative_prompts = negative_prompts

        for attack_type, attack_sprite in zip(attack_types, attack_sprites):
            self.attack_types[attack_type] = attack_sprite

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def add_negative_prompt(self, negative):
        self.negative_prompts.append(negative)

    def add_attack(self, attack_type, attack_sprite):
        if attack_type not in self.attack_types:
            self.attack_types[attack_type] = attack_sprite

class ImageGenerator:
    characters: List[Character]
    