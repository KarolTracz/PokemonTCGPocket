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

    card_pos = (1530, 225, 360, 515)
    # card_pos = (1560, 270, 340, 480)
    number_pos = (1596, 773, 40, 40)
    pokemon_templates_dir = r'C:\Users\karol.tracz\PycharmProjects\PokemonTCGPocket\pokemon_images'
    number_templates_dir = r'C:\Users\karol.tracz\PycharmProjects\PokemonTCGPocket\number_images'
    threshold = 0.65

    # # for debugging
    # pyautogui.moveTo(card_pos[0], card_pos[1])
    # pyautogui.moveTo(card_pos[0]+card_pos[2], card_pos[1], duration=1)
    # pyautogui.moveTo(card_pos[0]+card_pos[2], card_pos[1]+card_pos[3], duration=1)
    # sleep(2)
    # pyautogui.moveTo(number_pos[0], number_pos[1])
    # pyautogui.moveTo(number_pos[0]+number_pos[2], number_pos[1], duration=1)
    # pyautogui.moveTo(number_pos[0]+number_pos[2], number_pos[1]+number_pos[3], duration=1)
    # while True:
    #     print(pyautogui.position())
    #     pyautogui.sleep(3)
    #     move_card()
    # input('debugging break')

    count = 10

    while True:
        pyautogui.screenshot('./temp/number.png', region=number_pos)
        pyautogui.screenshot('./temp/temp.png', region=card_pos)
        sleep(1)

        try:
            img_path = os.path.join(pokemon_templates_dir, pokemon_tuple[count])
            print(f"{pokemon_tuple[count][:-11]}\t{round(compare_img(template_path=img_path, image_path='./temp/temp.png'), 2)}\t", end='')
            if compare_img(template_path=img_path, image_path='./temp/temp.png') > threshold:
                for number in os.listdir(number_templates_dir):
                    num_img = os.path.join(number_templates_dir, number)
                    if compare_img(template_path=num_img, image_path='./temp/number.png') > 0.9:
                        print(f"ADD {pokemon_tuple[count][:-11]}: {int(number[:-4])} ", end='')
                        result[pokemon_tuple[count][:-5]] = int(number[:-4])
                        move_card()
                        sleep(1)
            elif compare_img(template_path='./temp/not_obtained.png', image_path='./temp/temp.png') > 0.5:
                print(f"adding {pokemon_tuple[count][:-5]}: 0 ", end='')
                result[pokemon_tuple[count][:-5]] = 0
                move_card()
                sleep(1)
        except Exception as err:
            print(f'{err=}')

        if pokemon_tuple[count][:-5] not in result:
            print(f'NOT DETECTED {pokemon_tuple[count]}')
            result[pokemon_tuple[count][:-5]] = False
            move_card()
            sleep(1)


            # print('\n DEEPSCANING \n')
            # for name in os.listdir(pokemon_templates_dir):
            #     if compare_img(template_path=os.path.join(pokemon_templates_dir, name), image_path='./temp/temp.png') > threshold:
            #         for number in os.listdir(number_templates_dir):
            #             if compare_img(template_path=os.path.join(number_templates_dir, number), image_path='./temp/number.png') > 0.9:
            #                 print(f"adding {name[:-5]}: {int(number[:-4])}", end='')
            #                 result[name[:-5]] = int(number[:-4])
            #                 move_card()
            #                 sleep(1)
            #                 break
            #         if name not in result:
            #             result[name] = 10
            #         break
        else:
            print('SKIP')

        count += 1
        if count % 10 == 0:
            print(f'{result=}')


def move_card():
    pyautogui.moveTo(randrange(1750, 1850), randrange(840, 920))
    pyautogui.dragTo(randrange(1530, 1630), randrange(840, 920), duration=(randrange(4, 8)/10))


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
