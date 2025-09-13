from collections import Counter
from random import randrange
from time import sleep
from json import load, dumps
from os import listdir
from os.path import join as path_join
from subprocess import run
from math import floor
import sqlite3
import random

import cv2
from PIL import Image

with open('config.json', 'r') as f:
    config = load(f)

def main() -> None:
    # sets = get_all_sets(sql_db='PokeDB.db')
    # overall_counts, avg_per_card, avg_per_pack = simulate_many(trials=10_000, packs_per_trial=1000, have_pack_shinny=False)
    # print(overall_counts)
    # print(avg_per_card)
    # print(avg_per_pack)
    # print()
    # sum_bqy_set = {}
    # for set_num in sets:
    #     print(f'{set_num}')
    #     print(f'\t{sum_cards(set_num=set_num)}')
    #     print(f'{sum_cards_by_rarity(set_num=set_num)}')
    #     sum_by_set[set_num] = sum_cards_by_rarity(set_num=set_num)
    #
    # print(sum_by_set)
    # for k, v in sum_by_set.items():
    #     print(f'1_diamond: \t\t\t{v['1_diamond']}')
    #     print(f'1d/3 (packs):\t\t{v['1_diamond']/3:.2f}')
    #     print(f'wonder pick:\t\t{v['1_diamond']-(config[k]['points']/5*3)}')
    #     print(f'{k}| points from 1d\t{(v['1_diamond']/3*5):.2f}')
    #     print(f'{k}| config points\t{config[k]['points']}')
    #     print(f'diff:\t\t\t\t{v['1_diamond'] / 3 * 5-config[k]['points']:.2f}')
    #     print()
    while True:
        menu()


def menu() -> None:
    user_input = input("Input number"
                       "\n1. Scan whole card list"
                       "\n2. List amount of missing 1-4 diamond cards"
                       "\n3. Config setup "
                       "\n4. which_pack_open()"
                       "\n5. open_promo()"
                       "\n6. screenshot()\n")
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
        #TO-DO add change card_threshold value
        which_pack_open()
    elif user_input == 5:
        open_promo()
    elif user_input == 6:
        screenshot()

    else:
        pass
def claim_all_rewards() -> None:
    #TO-DO: Navigate to the rewards

    claim_all_pos = (700, 1940, 1000, 2020)
    x = str(randrange(claim_all_pos[0], claim_all_pos[2]))
    y = str(randrange(claim_all_pos[1], claim_all_pos[3]))

    run(["adb", "shell", "input", "tap", x, y])
    sleep(1)
    press_ok()


def open_promo() -> None:
    claim_all_rewards()

    claim_pos = (750, 580, 950, 650)
    x = str(randrange(claim_pos[0], claim_pos[2]))
    y = str(randrange(claim_pos[1], claim_pos[3]))
    run(["adb", "shell", "input", "tap", x, y])
    sleep(1)
    press_ok()


def press_ok() -> None:
    ok_pos=(375, 1475, 700, 1600)
    x = str(randrange(ok_pos[0], ok_pos[2]))
    y = str(randrange(ok_pos[1], ok_pos[3]))
    run(["adb", "shell", "input", "tap", x, y])


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

        progres_bar_width = 50
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

        print()
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


def screenshot_and_crop_card(img) -> None:
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
