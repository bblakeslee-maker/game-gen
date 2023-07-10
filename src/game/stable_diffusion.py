'''
1) Create interface for GPT prompt
2) Create a T pose character profile
3) Control character pose with control net, through automatic
4) Create character class to store the "likeness" of a character
    - Store the character description, negative prompts, T pose (front and back), and attack types
'''
import io
import random
import base64
import requests
import numpy as np
from PIL import Image
from tqdm import tqdm
from pathlib import Path
from typing import List, Dict
import cv2

SD_SERVER_IP = '172.30.0.94'


IMAGE_OUT_DIR = Path('/tmp/gamegen_img_cache')
IMAGE_OUT_DIR.mkdir(parents=True, exist_ok=True)

POSE_DIR = Path(__file__).parent / 'poses'
assert POSE_DIR.exists(), f"Can't find pose img dir: {POSE_DIR}"

SEED_MAX = 99999999

def retry(times, exceptions):
    """
    From: https://stackoverflow.com/questions/50246304/using-python-decorators-to-retry-request
    Retry Decorator
    Retries the wrapped function/method `times` times if the exceptions listed
    in ``exceptions`` are thrown
    :param times: The number of times to repeat the wrapped function/method
    :type times: Int
    :param Exceptions: Lists of exceptions that trigger a retry attempt
    :type Exceptions: Tuple of Exceptions
    """
    def decorator(func):
        def newfn(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    print(
                        'Exception thrown when attempting to run %s, attempt '
                        '%d of %d' % (func, attempt, times)
                    )
                    attempt += 1
            return func(*args, **kwargs)
        return newfn
    return decorator

class ImageObject:
    descriptors: List[str]
    front_pose: np.ndarray
    back_pose: np.ndarray
    negative_prompts: List[str]
    attack_types: Dict[str, np.ndarray]
    seed: int

    def __init__(
        self,
        descriptors,
        front_pose=None,
        back_pose=None,
        negative_prompts=None,
        attack_types=None,
        attack_sprites=None,
        seed=None,
    ):

        self.cache = IMAGE_OUT_DIR
        self.poses = POSE_DIR
        self.descriptors = descriptors
        self.front_pose = front_pose
        self.back_pose = back_pose
        self.negative_prompts = negative_prompts
        self.seed = seed

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


class ImageGenerator:
    def __init__(self):

        self.image_objects: Dict[str, ImageObject] = {}
        self.negative_prompts = [
            'blurry'
            'nudity',
            'sexy',
            'nsfw',
            'text',
            'written words',
            'letters',
            'words',
            'watermark'
        ]

        self.portrait_prompts = [
            'full color'
            'portrait',
            'head-shot',
            'face',
            'chest-up'
            'white background',
            'empty background',
            'plain background',
        ]

        override_settings = {
            'override_settings': {
                'filter_nsfw': True
            },
            'steps': 50
        }

        self.cache = IMAGE_OUT_DIR
        self.poses = []

        for file in POSE_DIR.glob('*jpg'):
            self.poses.append(file)

        # for file in self.cache.glob('*.png'):
        #     file.unlink()

        requests.post(url=f"http://{SD_SERVER_IP}:7860/sdapi/v1/options", json=override_settings)

    def create_character(self, name:str, description:str, no_bg:bool=False, look_right=False):
        descriptors = description.split(',')
        seed = random.randint(0, SEED_MAX)

        if name in self.image_objects:
            print('Character already exists. Skipping.')
        else:
            self.image_objects[name] = ImageObject(
                descriptors = descriptors,
                negative_prompts = self.negative_prompts,
                seed = seed,
            )

            self.get_portrait(name, no_bg=no_bg, look_right=look_right)

    def create_background(self, name:str, description:str):
        descriptors = description.split(',')

        if name in self.image_objects:
            print(f'Background {name} already exists. Skipping.')
        else:
            self.image_objects[name] = ImageObject(
                descriptors = descriptors,
                negative_prompts = self.negative_prompts,
            )

            self.get_background(name)

    @retry(3, [KeyError, requests.exceptions.ConnectTimeout])
    def get_background(self, name:str):
        if name not in self.image_objects:
            print(f'Background {name} does not exist')
            return

        file_name = self.cache / f'{name}.png'

        if file_name.exists():
            return str(file_name)

        pos_prompt = ['landscape', 'environment', 'terrain', 'scenery'] + self.image_objects[name].descriptors
        neg_prompt = ['people', 'characters', 'humans', 'crowd', 'person', 'animals', 'figures'] + self.image_objects[name].negative_prompts

        pos_prompt = ','.join(pos_prompt)
        neg_prompt = ','.join(neg_prompt)

        payload = {
            'prompt': pos_prompt,
            'negative_prompt': neg_prompt,
            'steps': 50,
            'batch_size': 1,
            'denoising_strength': 0.7,
            'hr_upscaler': "Nearest",
            'model': 'DPM++ 2M Kerras'
        }

        request_data = requests.post(url=f"http://{SD_SERVER_IP}:7860/sdapi/v1/txt2img", json=payload)
        request_data = request_data.json()

        img = request_data['images'][0]

        img = Image.open(io.BytesIO(base64.b64decode(img.split(",",1)[0])))
        img.save(file_name)

        return file_name

    def modify_character(self, name, description:str):
        descriptors = description.split(',')

        if name not in self.image_objects:
            print(f'Character {name} has not been created. Skipping')
        else:
            for descriptor in descriptors:
                self.image_objects[name].add_descriptor(descriptor)

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

    def get_portrait(self, name:str, no_bg:bool=False, look_right=False)->str:
        file_path = self.cache / f'{name}_portrait.png'

        if not file_path.exists():
            img = self.create_portrait(name, no_bg=no_bg, look_right=look_right)
            img.save(str(file_path))

        return str(file_path)

    @retry(3, [KeyError, requests.exceptions.ConnectTimeout])
    def create_portrait(self, name:str, no_bg:bool=False, look_right=False):
        if name not in self.image_objects:
            print(f'Character does not exist: {name}')
            return

        pos_prompt = self.image_objects[name].descriptors
        neg_prompt = self.image_objects[name].negative_prompts
        neg_prompt += [
            'bad anatomy',
            'amputations',
            'missing head',
            'body out of frame',
            'face out of frame',
            'shirtless',
            'disfigured',
            'kitsch',
            'ugly',
            'oversaturated',
            'grain',
            'low-res',
            'Deformed',
            'blurry',
            'bad anatomy',
            'disfigured',
            'poorly drawn face',
            'mutation',
            'mutated',
            'extra limb',
            'ugly',
            'poorly drawn hands',
            'missing limb',
            'blurry',
            'floating limbs',
            'disconnected limbs',
            'malformed hands',
            'blur',
            'out of focus',
            'long neck',
            'long body',
            'ugly',
            'disgusting',
            'poorly drawn',
            'childish',
            'mutilated',
            'mangled',
        ]

        pos_prompt = self.portrait_prompts + pos_prompt

        pos_prompt = ', '.join(pos_prompt)
        neg_prompt = ', '.join(neg_prompt)


        # Seed controlnet
        pose_file_name = random.choice(self.poses)
        pose_img = cv2.imread(str(pose_file_name))
        if look_right:
            pose_img = cv2.flip(pose_img, 1)

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

        if self.image_objects[name].seed is not None:
            payload['seed'] = self.image_objects[name].seed

        request_data = requests.post(url=f"http://{SD_SERVER_IP}:7860/sdapi/v1/txt2img", json=payload)
        request_data = request_data.json()

        img = request_data['images'][0]

        if no_bg:
            img = self.remove_bg(img)

        img = Image.open(io.BytesIO(base64.b64decode(img.split(",",1)[0])))

        return img

if __name__ == '__main__':
    '''
    Run this command for tunneling: ssh -t -N -L 7860:localhost:7860 vbanerjee@172.30.0.94
    '''

    gen = ImageGenerator()
    gen.create_character('dude', 'Gargantuan metallic beast with glowing eyes,Sinister tendrils reaching ominously,Eerie pulsating energy emanating,Armored with impenetrable titanium plates, Mouth dripping with acidic venom')

    portrait = gen.create_full_body('dude')

    for i,portrait in enumerate(portrait):
        portrait.save(f'img{i}.png')
