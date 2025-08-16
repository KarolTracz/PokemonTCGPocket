from random import randrange
from time import sleep
import json
import os
from typing import Tuple
import subprocess

import cv2
import pyautogui


with open('config.json', 'r') as f:
    config = json.load(f)

CARD_POS = tuple(config['card_pos'])
NUMBER_POS = tuple(config['number_pos'])


def main() -> None:
    move_card_new()
    input()
    print(f"{config=}")

    for k, v in config['sets'].items():
        print(k)
        # if k == 'a1' or k == 'a1a':
        #     continue
        result = count_set(set_starting_pos=v['start'], number_of_cards_in_set=v['all'], star_card=v['star'],
                           shiny_card=v['shiny'], crown_card=v['crown'])
        print(f'{k} {result=}')

        # Because star, shinny & crown not detected
        input('CHANGE SET')


def count_set(set_starting_pos: int, number_of_cards_in_set: int, star_card: int, shiny_card: int, crown_card: int) -> dict:

    result = {}

    number_templates_dir = r'C:\Users\karol.tracz\PycharmProjects\PokemonTCGPocket\number_images'

    number_threshold = 0.85
    count = 0

    while True:
        pyautogui.screenshot('./temp/number.png', region=NUMBER_POS)
        pyautogui.screenshot('./temp/temp.png', region=CARD_POS)
        sleep(1)

        number_ = 17
        for number in os.listdir(number_templates_dir)[::-1]:
            num_img = os.path.join(number_templates_dir, number)

            # print(number_)
            # print(f"{number} {round(compare_img(template_path=num_img, image_path='./temp/number.png'), 2)}")
            try:
                confidence = compare_img(template_path=num_img, image_path='./temp/number.png')
            except Exception as err:
                print(f'confidence set to 0 because of error{err=}')
                confidence = 0

            if confidence > number_threshold:
                print(f"{round(compare_img(template_path=num_img, image_path='./temp/number.png'), 2)}", end=' ')
                print(f"ADD {pokemon_tuple[set_starting_pos][:-5]} {count=}: {number_} ")
                result[pokemon_tuple[set_starting_pos][:-5]] = number_
                move_card()
                sleep(0.5)
                break

            number_ -= 1

        if compare_img(template_path='./temp/not_obtained.png', image_path='./temp/temp.png') > 0.5:
            print(f"{round(compare_img(template_path='./temp/not_obtained.png', image_path='./temp/temp.png'), 2)}", end=' ')
            print(f"ADD {pokemon_tuple[set_starting_pos][:-5]}=={count}: 0 ")
            result[pokemon_tuple[set_starting_pos][:-5]] = 0
            move_card()
            sleep(0.5)

        count += 1
        set_starting_pos += 1
        if count == number_of_cards_in_set:
            print(f'{count=} {set_starting_pos=}\n{result=}')
            return result
            # TO-DO break and go to deep scanning mode for star and crown cards, potentially separated in sets.


def debug_mode(card_pos: Tuple[int], number_pos: Tuple[int]):
    pyautogui.moveTo(card_pos[0], card_pos[1])
    pyautogui.moveTo(card_pos[0]+card_pos[2], card_pos[1], duration=1)
    pyautogui.moveTo(card_pos[0]+card_pos[2], card_pos[1]+card_pos[3], duration=1)
    sleep(1)
    pyautogui.moveTo(number_pos[0], number_pos[1])
    pyautogui.moveTo(number_pos[0]+number_pos[2], number_pos[1], duration=1)
    pyautogui.moveTo(number_pos[0]+number_pos[2], number_pos[1]+number_pos[3], duration=1)
    while True:
        print(pyautogui.position())
        pyautogui.sleep(3)
        move_card()


def move_card():
    pyautogui.moveTo(randrange(325, 390), randrange(835, 865))
    pyautogui.dragTo(randrange(10, 110), randrange(840, 920), duration=(randrange(4, 8)/10))

def move_card_new():
    x1, y1 = randrange(700, 1040), randrange(1850, 2175)
    x2, y2 = randrange(40, 380), randrange(1850, 2175)

    duration = randrange(4, 8)/10 * 1000

    subprocess.run([
        "adb", "shell", "input", "swipe",
        str(x1), str(y1), str(x2), str(y2), str(int(duration))
    ])

def compare_img(template_path: str, image_path: str):
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if template is None or image is None:
        return 0

    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)

    return max_val


def save_img(file_path: str, content):
    with open(file_path, 'wb') as f:
        f.write(content)


if __name__ == '__main__':
    main()
