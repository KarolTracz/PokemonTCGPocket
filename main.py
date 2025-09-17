from collections import Counter
from random import randrange
from time import sleep
from json import load, dumps
from os import listdir
from os.path import join as path_join
from subprocess import run
from typing import Tuple
from math import floor
from shutil import get_terminal_size
import sqlite3
import random

import cv2
from PIL import Image

with open('config.json', 'r') as f:
    config = load(f)

COLUMNS, ROWS = get_terminal_size()

def main() -> None:
    print(f'{ROWS=}, {COLUMNS=}')
    while True:
        menu()


def menu() -> None:
    if not is_scrcpy_on():
        print('scrcpy is off')
        exit()

    user_input = input("Input number\n"
                       "1. Scan whole card list\n"
                       "2. List amount of missing 1-4 diamond cards\n"
                       "3. Config setup\n"
                       "4. which_pack_open()\n"
                       "5. open_promo()\n"
                       "6. screenshot()\n"
                       "7. is_scrcpy_on()\n")
    if user_input == 'q':
        exit()
    try:
        user_input = int(user_input)
    except ValueError:
        print('Wrong value Bro :|')
        print('You need to put int')

    if user_input == 1:
        count_all_cards()
    elif user_input == 2:
        list_missing_cards()
    elif user_input == 3:
        config_setup()
    elif user_input == 4:
        #TO-DO: add change card_threshold value
        which_pack_open()
    elif user_input == 5:
        open_promo()
    elif user_input == 6:
        screenshot()
    elif user_input == 7:
        result = is_scrcpy_on()
        print(f'{result=}')
    else:
        pass


def press(position: Tuple[int, int, int, int]) -> None:
    """
    Press button that is in range from x1, y1 to x2 y2
    Where x1, y1 are top left corner of button position
    and x2, y2 are bottom right corner of button position
    all positions should be provided as an int representing number of pixel from left right corner of the screen
    """

    x = str(randrange(position[0], position[2]))
    y = str(randrange(position[1], position[3]))

    run(["adb", "shell", "input", "tap", x, y])


def claim_all_rewards() -> None:
    #TO-DO: Navigate to the rewards

    claim_all_pos = (700, 1940, 1000, 2020)
    ok_pos=(375, 1475, 700, 1600)

    press(position=claim_all_pos)
    sleep(2)
    press(position=ok_pos)


def is_scrcpy_on() -> bool:
    tasks_list = run("tasklist", capture_output=True, text=True).stdout
    if "scrcpy.exe" in tasks_list:
        scrcpy_is_running = True
    else:
        scrcpy_is_running = False
    return scrcpy_is_running


def open_promo() -> None:
    how_many_loop = input("Input how many promo pack you want to open\n")
    try:
        how_many_loop = int(how_many_loop)
    except ValueError:
        print('Invalid input, you need to provide int')
    first_reward_claim_pos = (750, 580, 950, 650)
    next_pos = (380, 2240, 700, 2340)
    tap_and_hold_pos = (940, 2270, 990, 2320)
    ok_pos = (375, 1475, 700, 1600)

    claim_all_rewards()
    for i in range(how_many_loop):
        press(position=first_reward_claim_pos)
        sleep(2)
        press(position=ok_pos)
        sleep(5)
        open_pack()
        sleep(5)
        press(position=tap_and_hold_pos)
        sleep(5)
        press(position=next_pos)
        sleep(5)
        press(position=ok_pos)
        sleep(2)


def open_pack() -> None:
    left_pos = (140, 1330, 180, 1370)
    right_pos = (900, 1330, 940, 1370)

    x1, y1 = str(randrange(left_pos[0], left_pos[2])), str(randrange(left_pos[1], left_pos[3]))
    x2, y2 = str(randrange(right_pos[0], right_pos[2])), str(randrange(right_pos[1], right_pos[3]))

    duration = randrange(2, 4) / 10 * 1000

    run([
        "adb", "shell", "input", "swipe",
        str(x2), str(y2), str(x1), str(y1), str(int(duration))
    ])


def which_pack_open(card_threshold: int = 1) -> None:
    con = sqlite3.connect('PokeDB.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    pokemons = cur.execute(f"SELECT * FROM normal_cards").fetchall()
    not_obtain_pokemons = {}
    seek_rarity = ('1_diamond', '2_diamond', '3_diamond', '4_diamond')
    for pokemon in pokemons:
        if pokemon['amount'] is None:
            print('You need to scan your whole collection, we dont have data for amount you have')
            break
        if pokemon['amount'] < card_threshold and pokemon['rarity'] in seek_rarity:
            if pokemon['set_num'] not in not_obtain_pokemons:
                not_obtain_pokemons[pokemon['set_num']] = 1
            else:
                not_obtain_pokemons[pokemon['set_num']] += 1
    print(not_obtain_pokemons.values())
    for k, v in not_obtain_pokemons.items():
        if v == max(not_obtain_pokemons.values()):
            print(k)
    con.close()


def simulate_many(trials: int, packs_per_trial: int, have_pack_shinny: bool):
    overall_counts = Counter()

    for _ in range(trials):
        overall_counts.update(open_X_packs(packs_per_trial, have_pack_shinny))

    total_packs = trials * packs_per_trial
    total_cards = total_packs * 5

    avg_per_card = {k: v / total_cards for k, v in overall_counts.items()}
    avg_per_pack = {k: v / total_packs for k, v in overall_counts.items()}

    return overall_counts, avg_per_card, avg_per_pack


def open_X_packs(amount: int, have_pack_shinny: bool):
    sum_list= ['1_diamond' for _ in range(3*amount)]

    if have_pack_shinny:
        gen_4 = roll_4th_card(is_shinny=True)
        gen_5 = roll_5th_card(is_shinny=True)
    else:
        gen_4 = roll_4th_card(is_shinny=False)
        gen_5 = roll_5th_card(is_shinny=False)

    for _ in range(amount):
        sum_list.append(next(gen_4))
        sum_list.append(next(gen_5))

    return Counter(sum_list)


def roll_5th_card(is_shinny: bool):
    if is_shinny:
        offering_rates = {'1_diamond': 0, '2_diamond': 0.56 , '3_diamond': 0.19810, '4_diamond': 0.06664, '1_star': 0.10288, '2_star': 0.02, '3_star': 0.00888, '1_shiny': 0.02857, '2_shiny': 0.01333, 'crown': 0.00160}
    else:
        offering_rates = {'1_diamond': 0, '2_diamond': 0.60, '3_diamond': 0.20, '4_diamond': 0.06664, '1_star': 0.10288, '2_star': 0.02, '3_star': 0.00888, 'crown': 0.00160}

    items, probs = zip(*offering_rates.items())
    cumulative = [sum(probs[:i+1]) for i in range(len(probs))]
    while True:
        roll = random.random()
        for item, threshold in zip(items, cumulative):
            if roll < threshold:
                yield item
                break


def roll_4th_card(is_shinny: bool):
    if is_shinny:
        offering_rates = {'1_diamond': 0, '2_diamond': 0.89, '3_diamond': 0.04952, '4_diamond': 0.01667, '1_star': 0.02572, '2_star': 0.005, '3_star': 0.00222, '1_shiny': 0.00714, '2_shiny': 0.00333, 'crown': 0.00040}
    else:
        offering_rates = {'1_diamond': 0, '2_diamond': 0.90, '3_diamond': 0.05, '4_diamond': 0.01666, '1_star': 0.02572, '2_star': 0.005, '3_star': 0.00222, 'crown': 0.0004}
    items, probs = zip(*offering_rates.items())
    cumulative = [sum(probs[:i+1]) for i in range(len(probs))]

    while True:
        roll = random.random()
        for item, threshold in zip(items, cumulative):
            if roll < threshold:
                yield item
                break


def sum_cards_by_rarity(set_num: str) -> dict:
    con = sqlite3.connect('PokeDB.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    pokemons = cur.execute(f"SELECT rarity, amount FROM normal_cards WHERE set_num = '{set_num}'").fetchall()

    return_dict = {}
    for pokemon in pokemons:
        if pokemon['rarity'] not in return_dict:
            return_dict[pokemon['rarity']] = pokemon['amount']
        else:
            return_dict[pokemon['rarity']] += pokemon['amount']
    con.close()
    return return_dict


def sum_cards(set_num: str) -> int:
    con = sqlite3.connect('PokeDB.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    pokemons = cur.execute(f"SELECT amount FROM normal_cards WHERE set_num = '{set_num}'").fetchall()
    return sum([pokemon['amount'] for pokemon in pokemons])


# Prob better to do this as a db instead of config, fine for now as a shortcut.
def config_setup():
    with open('config.json', 'r') as f:
        config = load(f)
        new_config = config.copy()
    for set_num in new_config.keys():
        points = input(f'input how much "Pack Point Exchange" you have for {set_num} ')
        try:
            new_config[set_num]['points'] = int(points)
        except ValueError:
            print('You need to provide')
    with open('config.json', 'w') as f:
        f.write(dumps(new_config, indent=4))


def list_missing_cards() -> None:
    con = sqlite3.connect('PokeDB.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    pokemons = cur.execute(f"SELECT * FROM normal_cards").fetchall()
    not_obtain_pokemons = {}
    seek_rarity = ('1_diamond', '2_diamond', '3_diamond', '4_diamond')
    for pokemon in pokemons:

        if pokemon['amount'] is None:
            print('You need to scan your whole collection, we dont have data for amount you have')
            break
        if pokemon['amount'] == 0 and pokemon['rarity'] in seek_rarity:
            if pokemon['set_num'] not in not_obtain_pokemons:
                not_obtain_pokemons[pokemon['set_num']] = {
                    k: v for k, v in zip(seek_rarity, (0 for _ in range(len(seek_rarity))))
                }
            else:
                not_obtain_pokemons[pokemon['set_num']][pokemon['rarity']] += 1
    for set_num, values in not_obtain_pokemons.items():
        print(set_num)
        for rarity, amount in values.items():
            print(f'{rarity}\t- {amount}')
    con.close()


def count_all_cards() -> None:
    sets = get_all_sets(sql_db='PokeDB.db')

    for set_num in sets:
        if input(f"prep for {set_num}. Input 'c' to skip this set. For count set press enter ").lower() == 'c':
            continue
        con = sqlite3.connect('PokeDB.db')
        cur = con.cursor()
        pokemons = cur.execute(f"SELECT * FROM normal_cards WHERE set_num = '{set_num}'").fetchall()

        progres_bar_width = COLUMNS - 20
        for i, pokemon in enumerate(pokemons):
            screenshot_and_crop_card()
            card_amount = count_card(threshold=0.95)
            move_card_forward()

            bar = '['
            progres = (i + 1) * 100 / len(pokemons)
            for _ in range(floor(progres * progres_bar_width / 100)):
                bar +='|'
            for _ in range(floor(progres * progres_bar_width / 100), progres_bar_width):
                bar += ' '
            bar += ']'
            print(f'\r{bar} {progres:06.2f}% \t{set_num}', end='', flush=True)

            if card_amount is None:
                print("\ncard_amount = None")
                move_card_backward()
                sleep(1)
                screenshot_and_crop_card()
                card_amount = count_card(threshold=0.95)
                print(pokemon[1], card_amount)
                sleep(1)
                move_card_forward()
            if card_amount == 0:
                cur.execute(f"UPDATE normal_cards SET amount = 0 WHERE id = {pokemon[0]};")
            elif card_amount >= 1:
                cur.execute(f"UPDATE normal_cards SET amount = {card_amount} WHERE id = {pokemon[0]};")
            else:
                print(f"\nUNEXPECTED BEHAVIOR OF count_card() -> {card_amount}")

        con.commit()
        con.close()


def count_card(threshold: float = 0.95) -> int | None:
    for number in listdir('images/numbers'):
        num_img = path_join('images/numbers', number)
        confidence = compare_img(template_path=num_img, image_path='./temp/number.png')
        if confidence > threshold:
            return int(number[:2])

    if compare_img(template_path='images/not_obtained.png', image_path='./temp/screen.png') > 0.5:
        return 0
    else:
        return None

def screenshot() -> None:
    with open('./temp/screen.png', "wb") as f:
        run(["adb", "exec-out", "screencap", "-p"], stdout=f)


def screenshot_and_crop_card() -> None:
    screenshot()
    img = Image.open("./temp/screen.png")
    crop_area = (235, 1727, 292, 1771)
    cropped_img = img.crop(crop_area)
    cropped_img.save("./temp/number.png")


def get_all_sets(sql_db: str):
    con = sqlite3.connect(sql_db)
    cur = con.cursor()
    res = set(cur.execute("SELECT set_num FROM normal_cards"))
    return_set = sorted({i[0] for i in res})
    return return_set

def move_card_backward():
    x1, y1 = randrange(700, 1000), randrange(1850, 2175)
    x2, y2 = randrange(40, 380), randrange(1850, 2175)

    duration = randrange(6, 8) / 10 * 1000

    run([
        "adb", "shell", "input", "swipe",
        str(x2), str(y2), str(x1), str(y1), str(int(duration))
    ])
    sleep(0.2)

def move_card_forward():
    x1, y1 = randrange(700, 1000), randrange(1850, 2175)
    x2, y2 = randrange(40, 380), randrange(1850, 2175)

    duration = randrange(6, 8) / 10 * 1000

    run([
        "adb", "shell", "input", "swipe",
        str(x1), str(y1), str(x2), str(y2), str(int(duration))
    ])
    sleep(0.2)


def compare_img(template_path: str, image_path: str):
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if template is None or image is None:
        return 0

    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)

    return max_val


if __name__ == '__main__':
    main()
