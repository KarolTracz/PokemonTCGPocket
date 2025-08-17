from random import randrange
from time import sleep
from json import load as json_load
from os import listdir
from os.path import join as path_join
from subprocess import run
import sqlite3

import cv2
from PIL import Image

with open('config.json', 'r') as f:
    config = json_load(f)


def main() -> None:
    sets = get_all_sets(sql_db='PokeDB.db')

    for set_num in sets:
        con = sqlite3.connect('PokeDB.db')
        cur = con.cursor()
        pokemons = cur.execute(f"SELECT * FROM normal_cards WHERE set_num = '{set_num}'").fetchall()

        for pokemon in pokemons:

            screenshot_and_crop_card()
            move_card()

            number_threshold = 0.95
            for number in listdir('images/numbers'):
                num_img = path_join('images/numbers', number)
                try:
                    confidence = compare_img(template_path=num_img, image_path='./temp/number.png')
                except Exception as err:
                    cur.execute(f"UPDATE normal_cards SET amount = 0 WHERE id = {pokemon[0]};")
                    print(f'confidence of {pokemon[1]=} set to 0 because of error{err=}')
                    confidence = 0
                if confidence > number_threshold:
                    print(f'{pokemon[1]} {int(number[:2])}')
                    cur.execute(f"UPDATE normal_cards SET amount = {int(number[:2])} WHERE id = {pokemon[0]};")
                    break

            if compare_img(template_path='images/not_obtained.png', image_path='./temp/screen.png') > 0.5:
                print(f'{pokemon[1]} SET = 0, because not obtained ')
                cur.execute(f"UPDATE normal_cards SET amount = 0 WHERE id = {pokemon[0]};")

        con.commit()
        con.close()


def count_set_new():
    pass


def screenshot_and_crop_card() -> None:
    with open('./temp/screen.png', "wb") as f:
        run(["adb", "exec-out", "screencap", "-p"], stdout=f)
    img = Image.open("./temp/screen.png")
    crop_area = (235, 1725, 292, 1769)
    cropped_img = img.crop(crop_area)
    cropped_img.save("./temp/number.png")


def get_all_sets(sql_db):
    con = sqlite3.connect(sql_db)
    cur = con.cursor()
    res = set(cur.execute("SELECT set_num FROM normal_cards"))
    return_set = sorted({i[0] for i in res})
    return return_set


def move_card():
    x1, y1 = randrange(700, 1040), randrange(1850, 2175)
    x2, y2 = randrange(40, 380), randrange(1850, 2175)

    duration = randrange(4, 8) / 10 * 1000

    run([
        "adb", "shell", "input", "swipe",
        str(x1), str(y1), str(x2), str(y2), str(int(duration))
    ])
    sleep(0.1)


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
