'''
1) Create interface for GPT prompt
2) Create a T pose character profile
3) Control character pose with control net, through automatic
4) Create character class to store the "likeness" of a character
    - Store the character description, negative prompts, T pose (front and back), and attack types
'''
import numpy as np
from PIL import Image
import requests, io, base64
from typing import List, Dict
from pprint import pprint

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

    def create_image(self, prompt:str):
        payload = {
            "prompt": prompt,
            "steps": 5
        }

        request_data = requests.post(url=f"http://127.0.0.1:7860/sdapi/v1/txt2img", json=payload)
        request_data = request_data.json()

        pprint(request_data)

        for i,img in enumerate(request_data['images']):
            image = Image.open(io.BytesIO(base64.b64decode(img.split(",",1)[0])))

            image.save(f'img{i}.png')


if __name__ == '__main__':
    prompt = 'Sun-kissed skin, weathered by sun, Calloused hands, testament to toil, Strong physique, built for labor, Rugged face, etched with determination, Deep-set eyes, filled with wisdom, Humble attire, clothes of simplicity, Earth-stained boots, treading firm ground, Farmers hat, shielding from sun, Grizzled beard, hinting of experience, Unassuming presence, extraordinary potential'

    gen = ImageGenerator()
    gen.create_image(prompt=prompt)
