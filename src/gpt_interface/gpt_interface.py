import dotenv
import os
import openai

dotenv.load_dotenv()

SYS_PROMPT = 'You are the narrator for an epic fantasy story.'


def main():
    with open(os.getenv('CHAT_GPT_KEY_FILE')) as f:
        api_key = f.read().strip()
    openai.api_key = api_key

    '''
    payload = [{'role': 'user', 'content': 'Can you recite "lorem ipsum"?'}]
    chat_completion = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=payload)
    print(chat_completion)
    for cc in chat_completion.choices:
        print(cc.message.content)
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


if __name__ == '__main__':
    main()
