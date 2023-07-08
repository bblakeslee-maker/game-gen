import dotenv
import os
import openai

dotenv.load_dotenv()

SYS_PROMPT = 'You are the narrator for an epic fantasy story.'


class StoryTeller:
    def __init__(self):
        self.BASE_PROMPT = 'Pretend you are the narrator of a video game.  Your job ' \
                           'is to generate plotlines for the story.'
        self.MODEL = 'gpt-3.5-turbo'
        self.get_basic_character_info()
        self.select_story_genre()
        self.create_prologue()
        self.create_final_boss()
        self.create_endings()

    def invoke_chatgpt(self, payload):
        response = openai.ChatCompletion.create(model=self.MODEL, messages=payload)
        return response.choices[0].message.content

    def get_basic_character_info(self):
        self.player_name = input('Enter a player name: ')
        self.player_job = input('Enter the player job: ')
        self.player_misc = input('Tell me anything extra about yourself: ')

    def select_story_genre(self):
        payload = [
            {'role': 'user',
             'content': f'Based on the character name {self.player_name}, '
                        f'their job {self.player_job}, and the additional '
                        f'information {self.player_misc}, what genre of story '
                        f'should be created?  Respond with a single word, '
                        f'like "fantasy" or "sci-fi"'}
        ]
        self.genre = self.invoke_chatgpt(payload)

    def create_prologue(self):
        payload = [
            {'role': 'system', 'content': self.BASE_PROMPT},
            {'role': 'user',
             'content': f'{self.player_name} is a {self.player_job} in a {self.genre} story.  '
                        f'Write a single paragraph prologue for the story.'}
        ]
        self.prologue = self.invoke_chatgpt(payload)

    def create_final_boss(self):
        payload = [
            {'role': 'system', 'content': self.prologue},
            {'role': 'user', 'content': f'Describe the appearance of a final boss that '
                                        f'{self.player_name} the {self.player_job} '
                                        f'needs to fight.  Describe it in five phrases,'
                                        f'each five words or fewer.'}
        ]
        self.final_boss_description = self.invoke_chatgpt(payload)
        payload = [
            {'role': 'system', 'content': self.final_boss_description},
            {'role': 'user', 'content': 'Describe this character in five phrases,'
                                        'each five words or fewer.'}
        ]
        self.final_boss_prompt = self.invoke_chatgpt(payload)

    def create_endings(self):
        payload = [
            {'role': 'system',
             'content': self.BASE_PROMPT + ' ' + self.prologue + ' ' + self.final_boss_description},
            {'role': 'user', 'content': f'Write a single paragraph ending for this story, '
                                        f'assuming that {self.player_name} is victorious.'}
        ]
        self.epilogue_victory = self.invoke_chatgpt(payload)
        payload = [
            {'role': 'system',
             'content': self.BASE_PROMPT + ' ' + self.prologue + ' ' + self.final_boss_description},
            {'role': 'user', 'content': f'Write a single paragraph ending for this story, '
                                        f'assuming that {self.player_name} loses the fight.'}
        ]
        self.epilogue_defeat = self.invoke_chatgpt(payload)

def main():
    with open(os.getenv('CHAT_GPT_KEY_FILE')) as f:
        api_key = f.read().strip()
    openai.api_key = api_key

    storyteller = StoryTeller()
    print('Genre: ', storyteller.genre)
    print('Prologue: ', storyteller.prologue)
    print('Boss Description: ', storyteller.final_boss_description)
    print('Boss Prompt: ', storyteller.final_boss_prompt)
    print('Epilogue Victory: ', storyteller.epilogue_victory)
    print('Epilogue Defeat: ', storyteller.epilogue_defeat)

    '''
    payload = [{'role': 'user', 'content': 'Can you recite "lorem ipsum"?'}]
    chat_completion = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=payload)
    print(chat_completion)
    for cc in chat_completion.choices:
        print(cc.message.content)
    '''

    '''
    player_name = input('Enter a player name: ')
    player_job = input('Enter the player job: ')
    player_dislikes = input('Enter some things you dislike: ')

    payload = [
        {'role': 'system',
         'content': SYS_PROMPT + '  Generate a plot summary.'},
        {'role': 'user',
         'content': f'The name of the hero is {player_name}.  They are a {player_job}.  '
                    f'They dislike {player_dislikes}.  Generate a prologue for the story.'}
    ]
    chat_completion = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=payload)
    print(chat_completion.choices[0].message.content)

    payload = [
        {'role': 'system', 'content': chat_completion.choices[0].message.content},
        {'role': 'user', 'content': f'Describe {player_name} appearance in 5 phrases, '
                                    f'each five words or less.  Only provide the phrases.  '
                                    f'Do not make a numbered list.'}
    ]
    chat_completion = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=payload)
    print('************************')
    prompt = chat_completion.choices[0].message.content
    prompt = prompt.replace('.', ', ').replace('\n', '')
    print(prompt)
    '''


if __name__ == '__main__':
    main()
