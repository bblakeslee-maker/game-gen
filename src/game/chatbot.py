#!/usr/bin/env python

import argparse
import dotenv
import os
import json
import openai
from .utils import persistent_cache

dotenv.load_dotenv()

STORY_CACHE = 'cache.pkl'


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


def extract_json(text):
    # Find the first occurrence of a JSON object in the text
    # print("Extracting JSON from text", text)
    # start = text.find('{')
    # end = text.rfind('}')
    # if start == -1 or end == -1:
    #     print("NO JSONN!!!!!!")
    #     return None
    # json_str = text[start:end+1]
    #
    #
    # print(json_str)
    json_str = text
    # Parse the JSON object and return it as a dictionary
    try:
        json_dict = json.loads(json_str)
        return json_dict
    except json.JSONDecodeError:
        print("json.JSONDecodeError", json_str)
        return None

class StoryTeller:
    def __init__(self, use_chatgpt):
        self.use_chatgpt = use_chatgpt
        if use_chatgpt:
            openai.api_key = os.getenv('CHAT_GPT_KEY')

        self.BASE_PROMPT = 'Pretend you are the narrator of a video game.  Your job ' \
                           'is to generate plotlines for the story.'
        self.PROMPT_FORMATTING = 'Format the phrases as a list like this:' \
                                 'set of words 1\n' \
                                 'set of words 2\n' \
                                 'until you generate enough phrases.'
        self.DIALOG_FORMATTING = 'Format the dialog like this: \n' \
                                 'name: line of dialogue\n' \
                                 'until you generate enough dialogue.'
        self.MODEL = 'gpt-3.5-turbo'

    @persistent_cache(STORY_CACHE)
    @retry(3, [openai.error.ServiceUnavailableError])
    def invoke_chatgpt(self, payload):
        response = openai.ChatCompletion.create(model=self.MODEL, messages=payload)
        return response.choices[0].message.content

    def add_basic_character_info(self, name, occupation, extra_info):
        self.player_name = name
        self.player_job = occupation
        self.player_misc = extra_info
        self.EXTRA_CONTEXT = f'This is extra context about the main character {self.player_name}: "{self.player_misc}"'


    def select_story_genre(self):
        payload = [
            {'role': 'user',
             'content': f'Based on the character name {self.player_name}, '
                        f'their job {self.player_job}, and the additional '
                        f'information {self.player_misc}, what genre of story '
                        f'should be created?  Respond with a list of three single words.'}
        ]
        temp = self.invoke_chatgpt(payload)
        self.genre = ''.join([i for i in temp if not i.isdigit()]).replace('.', '').replace('\n', '')

    def create_prologue(self):
        payload = [
            {'role': 'system', 'content': self.BASE_PROMPT},
            {'role': 'system', 'content': self.EXTRA_CONTEXT},
            {'role': 'user',
             'content': f'{self.player_name} is a {self.player_job} in a {self.genre} story '
                        f'with a {self.tone} style.  Write a single paragraph prologue for the story.'}
        ]
        self.prologue = self.invoke_chatgpt(payload)

    def select_artistic_tone(self):
        payload = [
            {'role': 'system', 'content': f'The genre of the story is {self.genre}'},
            {'role': 'user',
             'content': 'Describe the visual artistic style and mood of the above story in 3 or 4 words.'}
        ]
        temp = self.invoke_chatgpt(payload)
        self.tone = ''.join([i for i in temp if not i.isdigit()]).replace('.', '').replace('\n', '')

    def create_prologue_dialogue(self):
        payload = [
            {'role': 'system', 'content': self.prologue},
            {'role': 'user', 'content': f'Generate six lines of dialogue between {self.player_name} '
                                        f'and {self.final_boss_name} from immediately before they begin to fight.  ' +
                                        self.DIALOG_FORMATTING}
        ]
        self.prologue_dialogue = self.invoke_chatgpt(payload)

    def create_epilogue_dialogue(self):
        payload = [
            {'role': 'system', 'content': self.epilogue_victory},
            {'role': 'user', 'content': f'Generate six lines of dialogue between {self.player_name} '
                                        f'and {self.final_boss_name}, after {self.player_name} defeats '
                                        f'{self.final_boss_name} in combat.  ' + self.DIALOG_FORMATTING}
        ]
        self.epilogue_victory_dialogue = self.invoke_chatgpt(payload)
        payload = [
            {'role': 'system', 'content': self.epilogue_defeat},
            {'role': 'user', 'content': f'Generate six lines of dialogue between {self.player_name} '
                                        f'and {self.final_boss_name}, after {self.final_boss_name} defeats'
                                        f' {self.player_name} in combat.  ' + self.DIALOG_FORMATTING}
        ]
        self.epilogue_defeat_dialogue = self.invoke_chatgpt(payload)

    def create_main_character(self):
        payload = [
            {'role': 'system', 'content': self.prologue},
            {'role': 'user', 'content': f'Describe the appearance of '
                                        f'{self.player_name} the {self.player_job}.'}
        ]
        self.main_character_description = self.invoke_chatgpt(payload)
        payload = [
            {'role': 'system', 'content': self.main_character_description},
            {'role': 'user', 'content': f'Describe the {self.player_job} in five phrases, '
                                        f'each five words or fewer.  ' + self.PROMPT_FORMATTING +
                                        f'Do not refer to {self.player_name} by name, '
                                        f'only describe {self.player_name}\'s appearance.'}
        ]
        temp = self.invoke_chatgpt(payload)
        self.main_character_prompt = ''.join([i for i in temp if not i.isdigit()]).replace('.', '')
        payload = [
            {'role': 'system', 'content': self.main_character_description},
            {'role': 'user', 'content': f'Generate a list of four attacks that {self.player_name} uses.  '
                                        f'Format it as a list of JSON objects, where each JSON object '
                                        f'has "name", "damage", "accuracy", and "description" keys. '
                                        f'has value for the "damage" should be a single integer that is '
                                        f'positive if it deals damage and negative if it heals. '
                                        f'The value for the "description" key should be five words or less.'}
        ]
        self.main_character_attacks = extract_json(self.invoke_chatgpt(payload))
        payload = [
            {'role': 'system', 'content': self.main_character_description},
            {'role': 'user', 'content': f'Generate a list of two items that {self.player_name} uses.'
                                        f'Format it as a list of JSON objects, where each JSON object '
                                        f'has "name", "damage", and "description" keys.  One should '
                                        f'be a healing item, the other should damage the antagonist.  The '
                                        f'healing item should deal negative damage.  The value for the '
                                        f'"description" key should be five words or less.'}
        ]
        self.main_character_inventory = extract_json(self.invoke_chatgpt(payload))

    def create_final_boss(self):
        payload = [
            {'role': 'system', 'content': f'The story is "{self.prologue}".  The protagonist of the story is '
                                          f'{self.player_name}, who is {self.main_character_description}.'},
            {'role': 'user', 'content': f'Describe the antagonist that '
                                        f'{self.player_name} the {self.player_job} '
                                        f'will eventually fight in one paragraph.'}
        ]
        self.final_boss_description = self.invoke_chatgpt(payload)
        payload = [
            {'role': 'system', 'content': self.final_boss_description},
            {'role': 'user', 'content': 'Generate a name for the antagonist.'}
        ]
        self.final_boss_name = self.invoke_chatgpt(payload)
        payload = [
            {'role': 'system', 'content': f'The antagonist\'s name is '
                                          f'{self.final_boss_name}.  ' + self.final_boss_description},
            {'role': 'user', 'content': f'Describe this character in five phrases, '
                                        f'each five words or fewer.  ' + self.PROMPT_FORMATTING +
                                        f'Do not refer to {self.player_name}, only describe {self.final_boss_name}.'}
        ]
        temp = self.invoke_chatgpt(payload)
        self.final_boss_prompt = ''.join([i for i in temp if not i.isdigit()]).replace('.', '').replace(')', '')
        payload = [
            {'role': 'system', 'content': f'The antagonist\'s name is '
                                          f'{self.final_boss_name}.  ' + self.final_boss_description},
            {'role': 'user', 'content': f'Generate a list of four attacks that the antagonist uses.  '
                                        f'Format it as a list of JSON objects, where each JSON object '
                                        f'has "name", "damage", "accuracy" and "description" keys.'
                                        f'The value for the "description" key should be five words or less.'}
        ]
        self.final_boss_attacks = extract_json(self.invoke_chatgpt(payload))
        payload = [
            {'role': 'system', 'content': f'The antagonist\'s name is '
                                          f'{self.final_boss_name}.  ' + self.final_boss_description},
            {'role': 'user', 'content': f'Generate a list of two items that the antagonist uses.'
                                        f'Format it as a list of JSON objects, where each JSON object '
                                        f'has "name", "damage", and "description" keys.  One should '
                                        f'be a healing item, the other should damage {self.player_name}.  '
                                        f'The healing item should deal negative damage.  The value for the '
                                        f'"description" key should be five words or less.'}
        ]
        self.final_boss_inventory = extract_json(self.invoke_chatgpt(payload))

    def create_endings(self):
        payload = [
            {'role': 'system',
             'content': self.BASE_PROMPT + ' ' + self.prologue + ' ' + self.final_boss_description},
            {'role': 'system', 'content': self.EXTRA_CONTEXT},
            {'role': 'user', 'content': f'Write a single paragraph ending for this {self.genre} '
                                        f'story with {self.tone} tone, assuming that {self.player_name} is victorious.'
                                        f'Do not make a list of paragraphs.'}
        ]
        self.epilogue_victory = self.invoke_chatgpt(payload)
        payload = [
            {'role': 'system',
             'content': self.BASE_PROMPT + ' ' + self.prologue + ' ' + self.final_boss_description},
            {'role': 'system', 'content': self.EXTRA_CONTEXT},
            {'role': 'user', 'content': f'Write a single paragraph ending for this {self.genre} '
                                        f'story with {self.tone} tone, assuming that {self.player_name} loses the fight.'
                                        f'Do not make a list of paragraphs.'}
        ]
        self.epilogue_defeat = self.invoke_chatgpt(payload)

    def create_title_card_prompt(self):
        payload = [
            {'role': 'system',
             'content': f'The title is {self.title}, a story about {self.prologue}, with a genre {self.genre}, '
                        f'in a tone {self.tone}.'},
            {'role': 'user', 'content': f'Describe a title image for this story.'
                                        f'Use a list of five phrases, each five words or less.  ' +
                                        self.PROMPT_FORMATTING + f'Only describe the image, '
                                                                 f'do not refer to the characters.'}
        ]
        temp = self.invoke_chatgpt(payload)
        self.title_card_prompt = ''.join([i for i in temp if not i.isdigit()]).replace('.', '').replace(')', '')

    def create_battle_card_prompt(self):
        payload = [
            {'role': 'system', 'content': self.prologue + ' ' + self.main_character_description + ' ' + self.final_boss_description},
            {'role': 'user', 'content': f'Describe the battlefield between {self.player_name} '
                                        f'and {self.final_boss_name} in five phrases, each five words or less. ' +
                                        self.PROMPT_FORMATTING + f' Do not refer to {self.player_name} or '
                                                                 f'{self.final_boss_name}, only describe the background.'}
        ]
        temp = self.invoke_chatgpt(payload)
        self.battle_card_prompt = ''.join([i for i in temp if not i.isdigit()]).replace('.', '').replace(')', '')

    def create_prologue_card_prompt(self):
        payload = [
            {'role': 'system', 'content': self.prologue},
            {'role': 'user', 'content': f'Describe the scene depicted in this plot, in five phrases,'
                                        f'each five words or less.  ' + self.PROMPT_FORMATTING +
                                        f'Do not refer to {self.player_name} or {self.final_boss_name}, '
                                        f'only describe the background.'}
        ]
        temp = self.invoke_chatgpt(payload)
        self.prologue_card_prompt = ''.join([i for i in temp if not i.isdigit()]).replace('.', '').replace(')', '')

    def create_epilogue_victory_card_prompt(self):
        payload = [
            {'role': 'system', 'content': self.epilogue_victory},
            {'role': 'user', 'content': f'Describe the scene depicted in this plot, in five phrases,'
                                        f'each five words or less.  ' + self.PROMPT_FORMATTING +
                                        f'Do not refer to {self.player_name} or {self.final_boss_name}, '
                                        f'only describe the background.'}
        ]
        temp = self.invoke_chatgpt(payload)
        self.epilogue_victory_card_prompt = ''.join([i for i in temp if not i.isdigit()]).replace('.', '').replace(')', '')

    def create_epilogue_defeat_card_prompt(self):
        payload = [
            {'role': 'system', 'content': self.epilogue_defeat},
            {'role': 'user', 'content': f'Describe the scene depicted in this plot, in five phrases,'
                                        f'each five words or less.  ' + self.PROMPT_FORMATTING +
                                        f'Do not refer to {self.player_name} or {self.final_boss_name}, '
                                        f'only describe the background.'}
        ]
        temp = self.invoke_chatgpt(payload)
        self.epilogue_defeat_card_prompt = ''.join([i for i in temp if not i.isdigit()]).replace('.', '').replace(')', '')

    def create_title(self):
        payload = [
            {'role': 'system', 'content': self.prologue},
            {'role': 'user', 'content': 'Create a title for this story.'}
        ]
        self.title = self.invoke_chatgpt(payload)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--use_chatgpt', required=False, action='store_true',
                        help='Set to enable ChatGPT interface.')
    args = parser.parse_args()

    storyteller = StoryTeller(args.use_chatgpt)

    storyteller.add_basic_character_info("Bob", "Builder", "He can totally fix anything, except his marriage.")
    storyteller.generate_story()

    print('Title: \n' + storyteller.title + '\n')
    print('Genre: \n' + storyteller.genre + '\n')
    print('Tone: \n' + storyteller.tone + '\n')
    print('Title Prompt: \n' + storyteller.title_card_prompt + '\n')
    print('Prologue: \n' + storyteller.prologue + '\n')
    print('Prologue Dialogue: \n' + storyteller.prologue_dialogue + '\n')
    print('Prologue Prompt: \n' + storyteller.prologue_card_prompt + '\n')
    print('Main Character Description: \n' + storyteller.main_character_description + '\n')
    print('Main Character Prompt: \n' + storyteller.main_character_prompt + '\n')
    print('Main Character Attacks: \n' + storyteller.main_character_attacks + '\n')
    print('Main Character Inventory: \n' + storyteller.main_character_inventory + '\n')
    print('Boss Name: \n' + storyteller.final_boss_name + '\n')
    print('Boss Description: \n' + storyteller.final_boss_description + '\n')
    print('Boss Prompt: \n' + storyteller.final_boss_prompt + '\n')
    print('Boss Attacks: \n' + storyteller.final_boss_attacks + '\n')
    print('Boss Inventory: \n' + storyteller.final_boss_inventory + '\n')
    print('Battle Card Prompt: \n' + storyteller.battle_card_prompt + '\n')
    print('Epilogue Victory: \n' + storyteller.epilogue_victory + '\n')
    print('Epilogue Victory Dialogue: \n' + storyteller.epilogue_victory_dialogue + '\n')
    print('Epilogue Victory Prompt: \n' + storyteller.epilogue_victory_card_prompt + '\n')
    print('Epilogue Defeat: \n' + storyteller.epilogue_defeat + '\n')
    print('Epilogue Defeat Dialogue: \n' + storyteller.epilogue_defeat_dialogue + '\n')
    print('Epilogue Defeat Prompt: \n' + storyteller.epilogue_defeat_card_prompt + '\n')


if __name__ == '__main__':
    main()
