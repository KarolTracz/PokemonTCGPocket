import sqlite3
import json

with open('pokemon_list.json', 'r', encoding='utf-8') as f:
    raw_pokemon_list = json.load(f)


def main() -> None:
    pokemon_list = change_rarity(raw_pokemon_list)
    create_database(pokemon_list=pokemon_list)
    pass


def change_rarity(sorce_json: list) -> list:
    rarities = {
        '◊': '1_diamond',
        '◊◊': '2_diamond',
        '◊◊◊': '3_diamond',
        '◊◊◊◊': '4_diamond',
        '☆': '1_star',
        '☆☆': '2_star',
        '☆☆☆': '3_star',
        '♕': 'crown',
        'Promo': 'promo'
    }

    last_was_3star = False
    for pokemon in sorce_json:
        if pokemon['rarity'] == '♕':
            last_was_3star = False
        elif pokemon['rarity'] == '☆☆☆':
            last_was_3star = True
        elif pokemon['rarity'] == '☆' and last_was_3star == True:
            pokemon['rarity'] = '1_shiny'
        elif pokemon['rarity'] == '☆☆' and last_was_3star == True:
            pokemon['rarity'] = '2_shiny'

        for i in rarities.keys():
            if i == pokemon['rarity']:
                pokemon['rarity'] = rarities[i]

    return sorce_json


def create_database(pokemon_list: list) -> None:
    con = sqlite3.connect("PokeDB.db")
    cur = con.cursor()
    cur.execute("DROP TABLE promo_cards")
    cur.execute("DROP TABLE normal_carads")
    cur.execute("CREATE TABLE normal_carads (id, name, set_num, num, pack, rarity, amount, stage)")
    cur.execute("CREATE TABLE promo_cards (id, name, set_num, num, pack, rarity, amount, stage)")

    normal_carads = json2db_data_parser([i for i in pokemon_list if i['id'][:2] != 'pa'])
    promo_cards = json2db_data_parser([i for i in pokemon_list if i['id'][:2] == 'pa'])
    print(normal_carads[:100])
    print(promo_cards[:100])

    cur.executemany("INSERT INTO normal_carads VALUES (?, ?, ?, ?, ?, ?, ?, ?)", normal_carads)
    cur.executemany("INSERT INTO promo_cards VALUES (?, ?, ?, ?, ?, ?, ?, ?)", promo_cards)
    con.commit()


def json2db_data_parser(json: list) -> list:
    procesed_cards = []
    for i, pokemon in enumerate(json):
        _set, num = pokemon['id'].split('-')
        pokemon_data = (
            i,
            pokemon['name'],
            _set,
            num,
            pokemon['pack'],
            pokemon['rarity'],
            None,
            None
        )
        procesed_cards.append(pokemon_data)
    return procesed_cards


if __name__ == '__main__':
    main()
