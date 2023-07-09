#!/usr/bin/env python

import argparse
import dotenv
import os
import openai

from .utils import persistent_cache

dotenv.load_dotenv()

STORY_CACHE = 'cache.pkl'


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
    def invoke_chatgpt(self, payload):
        response = openai.ChatCompletion.create(model=self.MODEL, messages=payload)
        return response.choices[0].message.content

    def add_basic_character_info(self, name, occupation, extra_info):
        self.player_name = name
        self.player_job = occupation
        self.player_misc = extra_info

    def generate_story(self):
        self.select_story_genre()
        self.create_prologue()
        self.select_artistic_tone()
        self.create_prologue_dialogue()
        self.create_main_character()
        self.create_final_boss()
        self.create_endings()
        self.create_epilogue_dialogue()
        self.create_story_card_prompts()
        self.create_title()

    def select_story_genre(self):
        if self.use_chatgpt:
            payload = [
                {'role': 'user',
                 'content': f'Based on the character name {self.player_name}, '
                            f'their job {self.player_job}, and the additional '
                            f'information {self.player_misc}, what genre of story '
                            f'should be created?  Respond with a list of three single words.'}
            ]
            self.genre = self.invoke_chatgpt(payload)
        else:
            self.genre = 'Dark Comedy, Supernatural, Culinary'

    def create_prologue(self):
        if self.use_chatgpt:
            payload = [
                {'role': 'system', 'content': self.BASE_PROMPT},
                {'role': 'user',
                 'content': f'{self.player_name} is a {self.player_job} in a {self.genre} story.  '
                            f'Write a single paragraph prologue for the story.'}
            ]
            self.prologue = self.invoke_chatgpt(payload)
        else:
            self.prologue = \
                'In the dark and mysterious city of Ravenbrook, plagued by insatiable hunger and an ' \
                'uncanny craving for blood, a most unlikely protagonist emerges. Bob, an eccentric ' \
                'vampire with an impeccable sense of humor, finds himself trapped in a twisted mix ' \
                'of horror and hilarity. As he navigates through the shadows of Ravenbrook, Bob ' \
                'strives to unleash the true potential of his supernatural abilities while facing ' \
                'peculiar challenges that only a vampire chef could encounter. From satisfying ' \
                'the cravings of his insatiable undead appetite to battling rival ghouls for ' \
                'control of the culinary underworld, Bob\'s journey promises an unforgettable ' \
                'tale of dark comedy, supernatural absurdity, and mouthwatering dishes that will ' \
                'leave even the most stoic souls in stitches. Welcome to Bob\'s world, where ' \
                'culinary excellence meets the supernatural in a feast for the senses.'

    def select_artistic_tone(self):
        if self.use_chatgpt:
            payload = [
                {'role': 'system', 'content': self.prologue},
                {'role': 'user',
                 'content': 'Describe the visual artistic style and mood of the above story in 3 or 4 words.'}
            ]
            self.tone = self.invoke_chatgpt(payload)
        else:
            self.tone = 'Whimsical, Colorful, Lighthearted'


    def create_prologue_dialogue(self):
        if self.use_chatgpt:
            payload = [
                {'role': 'system', 'content': self.prologue},
                {'role': 'user', 'content': f'Generate six lines of dialogue between {self.player_name} '
                                            f'and the final boss from immediately before they begin to fight.  ' +
                                            self.DIALOG_FORMATTING}
            ]
            self.prologue_dialogue = self.invoke_chatgpt(payload)
        else:
            self.prologue_dialogue = \
                'Vignoth: "So, this is where it all ends, in the heart of darkness itself."\n' \
                'Final Boss: "Indeed, Vignoth, but you shall find no solace in defeating me."\n' \
                'Vignoth: "I\'ve faced creatures more powerful than you. You won\'t be an exception."\n' \
                'Final Boss: "You underestimate the darkness that flows within me, hunter."\n' \
                'Vignoth: "I\'m not afraid of darkness, I embrace it to bring light to this land."\n' \
                'Final Boss: "Your arrogance will be your downfall, Vignoth. Prepare for oblivion!"\n' \
                'Vignoth: "I have faced every challenge that came my way. You\'ll be no different, monster!"\n'


    def create_epilogue_dialogue(self):
        if self.use_chatgpt:
            payload = [
                {'role': 'system', 'content': self.epilogue_victory},
                {'role': 'user', 'content': f'Generate six lines of dialogue between {self.player_name} '
                                            f'and the final boss, after {self.player_name} defeats the final '
                                            f'boss in combat.  ' + self.DIALOG_FORMATTING}
            ]
            self.epilogue_victory_dialogue = self.invoke_chatgpt(payload)
            payload = [
                {'role': 'system', 'content': self.epilogue_defeat},
                {'role': 'user', 'content': f'Generate six lines of dialogue between {self.player_name} '
                                            f'and the final boss, after the final boss defeats {self.player_name} '
                                            f'in combat.  ' + self.DIALOG_FORMATTING}
            ]
            self.epilogue_defeat_dialogue = self.invoke_chatgpt(payload)
        else:
            self.epilogue_victory_dialogue = \
                'Vignoth: It\'s over, monster. Your reign of terror ends here.\n' \
                'Monster: (Roaring defiantly) You may have bested me, but others like me will rise.\n' \
                'Vignoth: Not as long as I\'m here to protect Eldoria. Your kind will learn to fear the hunters.\n' \
                'Monster: (Weakly) You can\'t stop the inevitable. Darkness will always find a way.\n' \
                'Vignoth: Perhaps, but with each victory, the light grows stronger. Eldoria will never succumb to your darkness.\n' \
                'Monster: (Whispering) You...cannot...escape...what lies...beyond...\n' \
                'Vignoth: (Grim determination) I will face whatever challenges come, for the sake of Eldoria. Goodbye, monster. May your existence fade into nothingness.'

            self.epilogue_defeat_dialogue = \
                'Vignoth: You... cannot... win! Eldoria... will... prevail!\n' \
                'Final Boss: (Laughs menacingly) Your feeble resistance ends here, Vignoth. The might of the behemoth will consume your world.\n' \
                'Vignoth: I may fall today, but Eldoria\'s flame will never be extinguished. Others will rise in my place and vanquish you!\n' \
                'Final Boss: Your bravado means nothing, hero. Your sacrifice will be in vain, as darkness descends upon your precious land.\n' \
                'Vignoth: Even in defeat, I stand tall against the horrors you bring. Eldoria will remember my name, and your reign will crumble.\n' \
                'Final Boss: Foolish mortal, your grand dreams mean nothing in the face of true power. Your legend will fade, and Eldoria will despair.\n' \
                'Vignoth: The light will always prevail over darkness. Remember my words, for they shall haunt you as I return stronger, in spirit if not in body.'

    def create_main_character(self):
        if self.use_chatgpt:
            payload = [
                {'role': 'system', 'content': self.prologue},
                {'role': 'user', 'content': f'Describe the appearance of '
                                            f'{self.player_name} the {self.player_job}.'}
            ]
            self.main_character_description = self.invoke_chatgpt(payload)
            payload = [
                {'role': 'system', 'content': self.main_character_description},
                {'role': 'user', 'content': f'Describe the {self.player_job} in five phrases, '
                                            f'each five words or fewer.  ' + self.PROMPT_FORMATTING}
            ]
            temp = self.invoke_chatgpt(payload)
            self.main_character_prompt = ''.join([i for i in temp if not i.isdigit()]).replace('.', '')
            payload = [
                {'role': 'system', 'content': self.main_character_description},
                {'role': 'user', 'content': f'Generate a list of four attacks that {self.player_name} uses.  '
                                            f'Format it as a list of JSON objects, where each JSON object '
                                            f'has "name", "damage", and "accuracy" keys.'}
            ]
            self.main_character_attacks = self.invoke_chatgpt(payload)
        else:
            self.main_character_description = \
                'Bob is not your typical vampire. Unlike the brooding and dashing creatures of the ' \
                'night often depicted in literature and films, Bob is a middle-aged, slightly ' \
                'overweight vampire with a receding hairline and a perpetual five-o\'clock shadow. ' \
                'He stands at an average height, with a slightly hunched posture that belies his ' \
                'centuries of undead existence. \n\nBob\'s attire is just as unconventional as his ' \
                'appearance. He often dons a worn-out chef\'s coat, covered in splatters of various ' \
                'sauces and spices, symbolizing both his culinary passion and his occupation as a ' \
                'vampire chef. His coat, once a crisp white, now bears the battle scars of countless ' \
                'cooking mishaps and culinary experiments gone awry. Bob completes his unique ensemble ' \
                'with a mismatched assortment of kitchen utensils hanging from his belt, ranging from ' \
                'wooden spoons to meat tenderizers and even a whisk, ready for any gourmet emergency. \n\n ' \
                'While he may not possess the typical vampire allure, Bob compensates with his infectious ' \
                'humor and mischievous grin. His eyes, a piercing shade of crimson, stand out against ' \
                'his pale, almost translucent skin. They display a mischievous twinkle, reflecting his ' \
                'irreverent nature and his penchant for finding humor in the darkest corners of ' \
                'Ravenbrook. \n\n Overall, Bob may not fit the mold of a traditional vampire, but his ' \
                'distinctive appearance and quirky personality make him a beloved and unforgettable ' \
                'character in the twisted world of Ravenbrook.'

            self.main_character_prompt = \
                'Unconventional, aging, culinary vampire\n' \
                'Hunched, hirsute, perpetually amused\n' \
                'Crimson eyes twinkle mischievously\n' \
                'Worn-out chef\'s coat tells tales\n' \
                'Irreverent humor, unforgettable character'

            self.main_character_attacks = '[{"name": "Hammer Slam","damage": 20,"accuracy": 90},' \
                                          '{"name": "Saw Slash","damage": 15,"accuracy": 95},' \
                                          '{"name": "Wrench Whack","damage": 10,"accuracy": 98},' \
                                          '{"name": "Drill Drill","damage": 25,"accuracy": 85}]'

    def create_final_boss(self):
        if self.use_chatgpt:
            payload = [
                {'role': 'system', 'content': self.prologue},
                {'role': 'user', 'content': f'Describe the appearance of a final boss that '
                                            f'{self.player_name} the {self.player_job} '
                                            f'needs to fight in one paragraph.'}
            ]
            self.final_boss_description = self.invoke_chatgpt(payload)
            payload = [
                {'role': 'system', 'content': self.final_boss_description},
                {'role': 'user', 'content': 'Describe this character in five phrases, '
                                            'each five words or fewer.  ' + self.PROMPT_FORMATTING}
            ]
            temp = self.invoke_chatgpt(payload)
            self.final_boss_prompt = ''.join([i for i in temp if not i.isdigit()]).replace('.', '').replace(')', '')
            payload = [
                {'role': 'system', 'content': self.final_boss_description},
                {'role': 'user', 'content': f'Generate a list of four attacks that the final boss uses.  '
                                            f'Format it as a list of JSON objects, where each JSON object '
                                            f'has "name", "damage", and "accuracy" keys.'}
            ]
            self.final_boss_attacks = self.invoke_chatgpt(payload)
        else:
            self.final_boss_description = \
                'The final boss that Bob the Vampire must confront is a towering and formidable ' \
                'figure known as Lord Vladimort, the Blood Moon Empress. Lord Vladimort is a ' \
                'mesmerizing sight to behold, exuding an aura of regal darkness and malevolence. ' \
                'With eyes as crimson as freshly spilled blood and a mane of raven-black hair ' \
                'cascading down to their broad, imposing shoulders, Lord Vladimort possesses a ' \
                'timeless and ethereal beauty. \n\nClad in a gracefully tattered cloak, woven ' \
                'from midnight black silk and adorned with intricate silver embroidery depicting ' \
                'macabre scenes of visceral delight, Lord Vladimort radiates an air of mystery and ' \
                'power. Their long, slender fingers seem to elongate into claw-like appendages, ' \
                'glinting ominously in the dim light. \n\nStanding at an imposing height, Lord ' \
                'Vladimort\'s lean and athletic build hints at their supernatural strength and ' \
                'agility. Their porcelain pale skin, almost translucent, contrasts sharply with ' \
                'the deep crimson hue of their perfectly symmetrical lips, forever stained with ' \
                'the remnants of countless feasts. \n\nBut perhaps the most striking feature of ' \
                'Lord Vladimort is their ever-shifting form. As Bob squares off against them, ' \
                'they seamlessly morph, flowing between human, bat, and mist-like manifestations, ' \
                'exploiting their shape-shifting abilities with both grace and ruthlessness. \n\n' \
                'Summoning the spirits of the night to their aid, Lord Vladimort commands a legion ' \
                'of phantom bats that flutter and dive around them, creating an eerie symphony of ' \
                'whispered squeaks and the whisper of wings. Each bat possesses glowing red eyes, ' \
                'mirroring the malevolence and hunger in their master\'s gaze. \n\n Lord ' \
                'Vladimort\'s mere presence sends a chilling shiver down Bob\'s spine, an imposing ' \
                'force that embodies the very essence of darkness and immortality. It is a battle ' \
                'of wits, culinary skill, and supernatural prowess, as Bob must face the ultimate ' \
                'challenge to claim his place as the true culinary master of Ravenbrook.'

            self.final_boss_prompt = \
                'Regal darkness, mesmerizing and malevolent\n' \
                'Crimson-eyed beauty of darkness\n' \
                'Shapeshifting form, ethereal and deadly\n' \
                'Commanding bats, spirits of night\n' \
                'Ultimate challenge in culinary supremacy'

            self.final_boss_attacks = '[{"name": "Steel Crusher","damage": 150,"accuracy": 80},' \
                                      '{"name": "Rivet Rockets","damage": 100,"accuracy": 90},' \
                                      '{"name": "Concrete Slam","damage": 120,"accuracy": 70},' \
                                      '{"name": "Flaming Wrecking Ball","damage": 200,"accuracy": 60}]'


    def create_endings(self):
        if self.use_chatgpt:
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
        else:
            self.epilogue_victory = \
                'With his quick thinking, culinary expertise, and uncanny sense of humor, Bob ' \
                'the Vampire chef manages to outwit Lord Vladimort, exploiting their weaknesses ' \
                'and using ingredients from the shadows to concoct a dish that overwhelms the ' \
                'Blood Moon Empress. As Lord Vladimort crumbles to the ground, their regal ' \
                'facade shattered, Bob stands triumphant, the true culinary master of Ravenbrook. ' \
                'The city is bathed in a new light as Bob\'s culinary creations bring joy and ' \
                'satiety to both humans and the undead alike, forever changing the culinary ' \
                'landscape of Ravenbrook with his undead flair and supernatural absurdity.'

            self.epilogue_defeat = \
                'As the final clash of their battle ensues, Bob\'s culinary skills prove to be no ' \
                'match for the raw power and ruthless cunning of Lord Vladimort. With a swift ' \
                'and calculated strike, Lord Vladimort decimates Bob\'s defenses, leaving him ' \
                'weakened and mortally wounded. The Blood Moon Empress, their lips curled in a ' \
                'sinister smile, lifts Bob\'s feeble body with a single elegant motion, ' \
                'relishing in their victory. With a whispered promise of eternal suffering, Lord ' \
                'Vladimort delivers a final blow that extinguishes Bob\'s existence, forever ' \
                'snuffing out the unique spark of humor and culinary genius that he brought to ' \
                'the dark streets of Ravenbrook. The city falls deeper into the shadows, under ' \
                'the iron grip of Lord Vladimort\'s relentless reign, haunted by the memory of ' \
                'that eccentric vampire chef who dared to challenge their authority.'

    def create_story_card_prompts(self):
        if self.use_chatgpt:
            payload = [
                {'role': 'system', 'content': self.prologue},
                {'role': 'user', 'content': 'Describe the scene depicted in this plot, in five phrases,'
                                            'each five words or less.  ' + self.PROMPT_FORMATTING}
            ]
            temp = self.invoke_chatgpt(payload)
            self.prologue_card_prompt = ''.join([i for i in temp if not i.isdigit()]).replace('.', '').replace(')', '')

            payload = [
                {'role': 'system', 'content': self.epilogue_victory},
                {'role': 'user', 'content': 'Describe the scene depicted in this plot, in five phrases,'
                                            'each five words or less.  ' + self.PROMPT_FORMATTING}
            ]
            temp = self.invoke_chatgpt(payload)
            self.epilogue_victory_card_prompt = ''.join([i for i in temp if not i.isdigit()]).replace('.', '').replace(')', '')

            payload = [
                {'role': 'system', 'content': self.epilogue_defeat},
                {'role': 'user', 'content': 'Describe the scene depicted in this plot, in five phrases,'
                                            'each five words or less.  ' + self.PROMPT_FORMATTING}
            ]
            temp = self.invoke_chatgpt(payload)
            self.epilogue_defeat_card_prompt = ''.join([i for i in temp if not i.isdigit()]).replace('.', '').replace(')', '')
        else:
            self.prologue_card_prompt = \
                'Dark city plagued by hunger\n' \
                'Eccentric vampire chef\'s journey\n' \
                'Horror and hilarity entwined\n' \
                'Supernatural abilities and challenges\n' \
                'Culinary excellence meets the supernatural'

            self.epilogue_victory_card_prompt = \
                'Bob outwits vampire lord\n' \
                'Culinary triumph over evil\n' \
                'Shadows yield extraordinary ingredients\n' \
                'Blood Moon Empress defeated\n' \
                'Ravenbrook transformed by immortal chef'

            self.epilogue_defeat_card_prompt = \
                'Culinary battle of epic proportions\n' \
                'Bob\'s defenses crumble, weakened\n' \
                'Blood Moon Empress revels victorious\n' \
                'Whispered promise of eternal suffering\n' \
                'City succumbs to Vladimort\'s reign'

    def create_title(self):
        if self.use_chatgpt:
            payload = [
                {'role': 'system', 'content': self.prologue},
                {'role': 'user', 'content': 'Create a title for this story.'}
            ]
            self.title = self.invoke_chatgpt(payload)
        else:
            self.title = '"Fangs and Flambé: The Hilarious Adventures of Bob the Vampire Chef"'

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
    print('Prologue: \n' + storyteller.prologue + '\n')
    print('Prologue Dialogue: \n' + storyteller.prologue_dialogue + '\n')
    print('Prologue Prompt: \n' + storyteller.prologue_card_prompt + '\n')
    print('Main Character Description: \n' + storyteller.main_character_description + '\n')
    print('Main Character Prompt: \n' + storyteller.main_character_prompt + '\n')
    print('Main Character Attacks: \n' + storyteller.main_character_attacks + '\n')
    print('Boss Description: \n' + storyteller.final_boss_description + '\n')
    print('Boss Prompt: \n' + storyteller.final_boss_prompt + '\n')
    print('Boss Attacks: \n' + storyteller.final_boss_attacks + '\n')
    print('Epilogue Victory: \n' + storyteller.epilogue_victory + '\n')
    print('Epilogue Victory Dialogue: \n' + storyteller.epilogue_victory_dialogue + '\n')
    print('Epilogue Victory Prompt: \n' + storyteller.epilogue_victory_card_prompt + '\n')
    print('Epilogue Defeat: \n' + storyteller.epilogue_defeat + '\n')
    print('Epilogue Defeat Dialogue: \n' + storyteller.epilogue_defeat_dialogue + '\n')
    print('Epilogue Defeat Prompt: \n' + storyteller.epilogue_defeat_card_prompt + '\n')


if __name__ == '__main__':
    main()
