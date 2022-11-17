"""
    Hello dictionary for our bot.
"""
import random

rand_hello_message_table = ['Neko Neko ( ⓛ ω ⓛ *)!',
                            'Hewo!',
                            'Be our senpai?',
                            'Wai senpai choose us to say hewo to??!?!?',
                            'Ano? WAAAAaaaahhh!!?!!? Senpai noticed us!?!',
                            'YaY!!!! (°ロ°)☝',
                            'BE OUR SENPAI!!!',
                            'WEN WE GROW AWP, WE WANNA BE WID SENPAI-KUN!!',
                            'Baka baka!! Senpai muss nao be pulverise by us!!',
                            'No one will conquer us!!!',
                            'Does senpai want us??',
                            'Hewo senpai!',
                            'https://www.youtube.com/watch?v=CKKj3uVImac']


rand_joining_message_table = ['Senpai, we have joined your channel!',
                              'We join your channel!',
                              'Senpai calls us to their channel!',
                              'Your onee sans come to your aid!']

rand_hentai_pic_table = [
    'going-blind.jpg',
    'l2s4jfiqmle61.jpg',
    'fap-til-blind.jpg'
]

rand_leaving_message_table = []

rand_moving_message_table = []


def get_hentai_img() -> str:
    return rand_hentai_pic_table[random.randint(0, len(rand_hentai_pic_table) - 1)]


def get_joining_message() -> str:
    return rand_joining_message_table[random.randint(0, len(rand_joining_message_table) - 1)]


def get_hello_message() -> str:
    '''
    Send a hello message!
    :return:
    '''
    return rand_hello_message_table[random.randint(0, len(rand_hello_message_table) - 1)]
