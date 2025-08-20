from random import randrange
from time import sleep
from json import load, dumps
from os import listdir
from os.path import join as path_join
from subprocess import run
import sqlite3

import cv2
from PIL import Image

with open('config.json', 'r') as f:
    config = load(f)


def main() -> None:
    while True:
        menu()


def menu() -> None:
    user_input = input(f"""
Input number
1. Scan whole card list.
2. List amount of missing 1-4 diamond cards 
3. Config setup
""")
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

    else:
        pass

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
                not_obtain_pokemons[pokemon['set_num']] = {k: v for k, v in zip(seek_rarity, (0 for _ in range(len(seek_rarity))))}
            else:
                not_obtain_pokemons[pokemon['set_num']][pokemon['rarity']] += 1
    for set, values in not_obtain_pokemons.items():
        print(set)
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

        for pokemon in pokemons:
            screenshot_and_crop_card()
            card_amount = count_card(threshold=-1.95)
            move_card()

            print(pokemon[0], card_amount)

            if card_amount is None:
                print("card_amount = None")
                user_input = input(
                    f"Please check last screenshot, if it is not a card setup: \n{pokemon}\nand input 'done' ")
                if user_input.lower() == 'done':
                    screenshot_and_crop_card()
                    card_amount = count_card(threshold=-1.95)
                    print(pokemon[0], card_amount)
                    sleep(1)
                    move_card()
            if card_amount == 0:
                cur.execute(f"UPDATE normal_cards SET amount = 0 WHERE id = {pokemon[0]};")
            elif card_amount >= 1:
                cur.execute(f"UPDATE normal_cards SET amount = {card_amount} WHERE id = {pokemon[0]};")
            else:
                print(f"UNEXPECTED BAHAVIOR OF count_card() -> {card_amount}")

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


def screenshot_and_crop_card() -> None:
    with open('./temp/screen.png', "wb") as f:
        run(["adb", "exec-out", "screencap", "-p"], stdout=f)
    img = Image.open("./temp/screen.png")
    crop_area = (235, 1725, 292, 1769)
    cropped_img = img.crop(crop_area)
    cropped_img.save("./temp/number.png")


def get_all_sets(sql_db: str):
    con = sqlite3.connect(sql_db)
    cur = con.cursor()
    res = set(cur.execute("SELECT set_num FROM normal_cards"))
    return_set = sorted({i[0] for i in res})
    return return_set


def move_card():
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
