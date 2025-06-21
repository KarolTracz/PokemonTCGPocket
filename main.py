from random import randrange
from time import sleep
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from data import pokemon_tuple

from requests import get, RequestException
import os
import cv2
import pyautogui

with open('old.html', 'r') as f:
    raw_source = f.read()


def main():
    # print(process_multiple_cards(raw_source))
    # input('break')

    result = {}

    card_pos = (25, 225, 360, 500)
    number_pos = (85, 770, 30, 30)

    # debug_mode(card_pos, number_pos)

    pokemon_templates_dir = r'C:\Users\karol.tracz\PycharmProjects\PokemonTCGPocket\pokemon_images'
    number_templates_dir = r'C:\Users\karol.tracz\PycharmProjects\PokemonTCGPocket\number_images'

    number_threshold = 0.85
    count = 0

    while True:
        pyautogui.screenshot('./temp/number.png', region=number_pos)
        pyautogui.screenshot('./temp/temp.png', region=card_pos)
        sleep(0.5)

        try:
            # print(os.listdir(number_templates_dir)[::-1])
            number_ = 13
            for number in os.listdir(number_templates_dir)[::-1]:
                num_img = os.path.join(number_templates_dir, number)
                print(number_)
                # print(f"{number} {round(compare_img(template_path=num_img, image_path='./temp/number.png'), 2)}")
                if compare_img(template_path=num_img, image_path='./temp/number.png') > number_threshold:
                    print(f"{round(compare_img(template_path=num_img, image_path='./temp/number.png'), 2)}", end=' ')
                    print(f"ADD {pokemon_tuple[count][:-5]}=={count}: {number_} ")
                    result[pokemon_tuple[count][:-5]] = number_
                    move_card()
                    sleep(0.8)
                    break
                number_ -= 1

            if compare_img(template_path='./temp/not_obtained.png', image_path='./temp/temp.png') > 0.7:
                print(f"{round(compare_img(template_path='./temp/not_obtained.png', image_path='./temp/temp.png'), 2)}", end=' ')
                print(f"ADD {pokemon_tuple[count][:-5]}=={count}: 0 ")
                result[pokemon_tuple[count][:-5]] = 0
                move_card()
                sleep(0.8)

        except Exception as err:
            print(f'{err=}')

        count += 1
        if count % 5 == 0:
            print(f'{count}\t{result=}')

        if count == 226:
            print(f'{count}\t{result=}')
            break


def debug_mode(card_pos, number_pos):
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


def compare_img(template_path, image_path):
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if template is None or image is None:
        return 0

    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)

    return max_val


def save_img(file_path, content):
    with open(file_path, 'wb') as f:
        f.write(content)


def extract_pokemon_data(html_content, save_directory="pokemon_images"):
    """
    Extract Pokemon name and image from HTML div, download image, and return dict
    """
    os.makedirs(save_directory, exist_ok=True)

    soup = BeautifulSoup(html_content, 'html.parser')

    name = soup.find('figcaption').text.strip().replace(' ', '_')
    set_code = soup.find('a')['href'].split('/')[2]
    card_number = soup.find('a')['href'].split('/')[3]
    img_link = soup.find('img')['src']

    if not name or not img_link:
        return None
    try:
        response = get(img_link)
        response.raise_for_status()

        parsed_url = urlparse(img_link)
        file_extension = os.path.splitext(parsed_url.path)[1]
        if not file_extension:
            file_extension = '.webp'

        filename = f"{name.lower()}_{set_code.lower()}_{card_number}{file_extension}"
        print(filename)
        file_path = os.path.join(save_directory, filename)
        # save_img(file_path, response.content)

        return filename

    except RequestException as e:
        print(f"Error downloading image for {name}: {e}")
        return None


def process_multiple_cards(html_content):
    """Process multiple Pokemon cards from HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    cards = []

    card_divs = soup.find_all('div', class_='card-grid__cell')

    for div in card_divs:
        result = extract_pokemon_data(str(div))
        if result:
            cards.append(result)

    return cards


if __name__ == '__main__':
    main()
