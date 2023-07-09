'''
1) Create interface for GPT prompt
2) Create a T pose character profile
3) Control character pose with control net, through automatic
4) Create character class to store the "likeness" of a character
    - Store the character description, negative prompts, T pose (front and back), and attack types
'''
import io
import base64
import requests
import numpy as np
from PIL import Image
from tqdm import tqdm
from io import BytesIO
from pathlib import Path
from typing import List, Dict
import plotly.express as px
import cv2

SD_SERVER_IP = '172.30.0.94'


CACHE_DIR = Path('/tmp/gamegen_img_cache')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

POSE_DIR = Path(__file__).parent / 'poses'
assert POSE_DIR.exists(), f"Can't find pose img dir: {POSE_DIR}"


class Character:
    descriptors: List[str]
    front_pose: np.ndarray
    back_pose: np.ndarray
    negative_prompts: List[str]
    attack_types: Dict[str, np.ndarray]

    def __init__(
        self,
        descriptors,
        front_pose=None,
        back_pose=None,
        negative_prompts=None,
        attack_types=None,
        attack_sprites=None,
    ):

        self.cache = CACHE_DIR
        self.poses = POSE_DIR
        self.descriptors = descriptors
        self.front_pose = front_pose
        self.back_pose = back_pose
        self.negative_prompts = negative_prompts

        self.cache.mkdir(exist_ok=True, parents=True)

        if negative_prompts is None:
            negative_prompts = []
        if attack_types is None:
            attack_types = []
        if attack_sprites is None:
            attack_sprites = []

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
    def __init__(self):

        self.characters: Dict[str, Character] = {}
        self.negative_prompts = [
            'bad anatomy',
            'amputations',
            'missing head',
            'body out of frame',
            'face out of frame',
            'shirtless',
            'blurry'
            'nudity',
            'sexy',
            'nsfw',
        ]

        self.portrait_prompts = [
            'full color'
            'portrait',
            'head-shot',
            'face',
            'chest-up'
        ]

        self.full_body_prompts = [
            'full color'
            'full-body shot',
        ]

        override_settings = {
            'override_settings': {
                'filter_nsfw': True
            },
            'steps': 50
        }

        self.cache = CACHE_DIR
        self.poses = POSE_DIR

        for file in self.cache.glob('*.png'):
            file.unlink()

        requests.post(url=f"http://{SD_SERVER_IP}:7860/sdapi/v1/options", json=override_settings)

    def create_character(self, name:str, description:str):
        descriptors = description.split(',')

        if name in self.characters:
            print('Character already exists. Skipping.')
        else:
            self.characters[name] = Character(
                descriptors = descriptors,
                negative_prompts = self.negative_prompts
            )

            self.get_portrait(name)

    def modify_character(self, name, description:str):
        descriptors = description.split(',')

        if name not in self.characters:
            print('Character has not been created. Skipping')
        else:
            for descriptor in descriptors:
                self.characters[name].add_descriptor(descriptor)

    def remove_bg(self, image:str):
        payload = {
            "input_image": image,
            "model": "isnet-general-use",
            "return_mask": False,
            "alpha_matting": False,
            "alpha_matting_foreground_threshold": 240,
            "alpha_matting_background_threshold": 10,
            "alpha_matting_erode_size": 10
        }

        request_data = requests.post(url=f"http://{SD_SERVER_IP}:7860/rembg", json=payload)
        request_data = request_data.json()

        return request_data['image']

    def create_full_body(self, name:str, no_bg:bool=False):
        if name not in self.characters:
            print(f'Character does not exist: {name}')
            return

        pos_prompt = self.characters[name].descriptors
        neg_prompt = self.characters[name].negative_prompts

        pos_prompt = self.full_body_prompts + pos_prompt + ['plane background']
        neg_prompt =  neg_prompt + ['missing torso', 'missing legs', 'missing arms', 'noisy background']

        pos_prompt = ','.join(pos_prompt)
        neg_prompt = ','.join(neg_prompt)

        payload = {
            'prompt': pos_prompt,
            'negative_prompt': neg_prompt,
            'steps': 50,
            'restore_faces': True,
            'batch_size': 1,
            'denoising_strength': 0.7,
            'hr_upscaler': "Nearest",
            'model': 'DPM++2M'
        }

        print('Generating images')
        request_data = requests.post(url=f"http://{SD_SERVER_IP}:7860/sdapi/v1/txt2img", json=payload)
        request_data = request_data.json()

        images = []

        for img in tqdm(request_data['images']):
            if no_bg:
                img = self.remove_bg(img)

            img = Image.open(io.BytesIO(base64.b64decode(img.split(",",1)[0])))
            images.append(img)

        return images

    def get_portrait(self, name:str)->str:
        file_path = self.cache / f'{name}_portrait.png'

        if not file_path.exists():
            img = self.create_portrait(name)[0]
            img.save(str(file_path))

        return str(file_path)

    def create_portrait(self, name:str, no_bg:bool=False):
        if name not in self.characters:
            print(f'Character does not exist: {name}')
            return

        pos_prompt = self.characters[name].descriptors
        neg_prompt = self.characters[name].negative_prompts

        pos_prompt = self.portrait_prompts + pos_prompt

        pos_prompt = ','.join(pos_prompt)
        neg_prompt = ','.join(neg_prompt)


        # Seed controlnet
        pose_file_name = self.poses / f'3_4th_profile_pose' / 'source_img.png'
        pose_img = cv2.imread(str(pose_file_name))
        _, bytes = cv2.imencode('.png', pose_img)
        pose_img = base64.b64encode(bytes).decode('utf-8')

        payload = {
            'prompt': pos_prompt,
            'negative_prompt': neg_prompt,
            'steps': 50,
            'restore_faces': True,
            'batch_size': 1,
            'denoising_strength': 0.7,
            'hr_upscaler': "Nearest",
            "alwayson_scripts": {
                "controlnet":{
                    "args":[
                        {
                        "input_image": pose_img,
                        'module': 'openpose',
                        "model": "control_v11p_sd15_openpose [cab727d4]"
                        }
                    ]
                }
            }
        }

        print('Generating images')
        request_data = requests.post(url=f"http://{SD_SERVER_IP}:7860/sdapi/v1/txt2img", json=payload)
        request_data = request_data.json()

        images = []

        for img in tqdm(request_data['images']):
            if no_bg:
                img = self.remove_bg(img)

            img = Image.open(io.BytesIO(base64.b64decode(img.split(",",1)[0])))
            images.append(img)

        return images

if __name__ == '__main__':
    '''
    Run this command for tunneling: ssh -t -N -L 7860:localhost:7860 vbanerjee@172.30.0.94
    '''

    gen = ImageGenerator()
    gen.create_character('dude', 'Gargantuan metallic beast with glowing eyes,Sinister tendrils reaching ominously,Eerie pulsating energy emanating,Armored with impenetrable titanium plates, Mouth dripping with acidic venom')

    portrait = gen.create_full_body('dude')

    for i,portrait in enumerate(portrait):
        portrait.save(f'img{i}.png')
