import sqlite3
import json

with open('pokemon_list.json', 'r', encoding='utf-8') as f:
    raw_pokemon_list = json.load(f)


def main() -> None:
    # pokemon_list = change_rarity(raw_pokemon_list)
    # create_database(pokemon_list=pokemon_list)
    # add_card_2_database(pokemon_list)
    alt_detection()


def alt_detection() -> None:
    con = sqlite3.connect("PokeDB.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    raw_normal_cards = cur.execute("SELECT * FROM normal_cards").fetchall()
    for pokemon_1 in raw_normal_cards:
        alts = []
        for pokemon_2 in raw_normal_cards:
            if pokemon_1['name'] == pokemon_2['name'] and pokemon_1['id'] != pokemon_2['id']:
                alts.append(pokemon_2['id'])

        print(f'SET alt_ids = {alts} WHERE id = {pokemon_1['id']};')
        cur.execute(f"UPDATE normal_cards SET alt_ids = '{alts}' WHERE id = {pokemon_1['id']};")
    con.commit()


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

def add_card_2_database(pokemon_list: list):
    con = sqlite3.connect("PokeDB.db")
    cur = con.cursor()

    raw_normal_cards = cur.execute("SELECT * FROM normal_cards").fetchall()
    normal_cards_in_db = []
    for i in raw_normal_cards:
        i = list(i)
        i[6] = None
        normal_cards_in_db.append(tuple(i))
    normal_cards = json2db_data_parser([i for i in pokemon_list if i['id'][:2] != 'pa'])
    new_normal_cards = [i for i in normal_cards if i not in normal_cards_in_db]

    raw_promo_cards = cur.execute("SELECT * FROM promo_cards").fetchall()
    promo_cards_in_db = []
    for i in raw_promo_cards:
        i = list(i)
        i[6] = None
        promo_cards_in_db.append(tuple(i))
    promo_cards = json2db_data_parser([i for i in pokemon_list if i['id'][:2] == 'pa'])
    new_promo_cards = [i for i in promo_cards if i not in promo_cards_in_db]

    cur.executemany("INSERT INTO normal_cards VALUES (?, ?, ?, ?, ?, ?, ?, ?)", new_normal_cards)
    cur.executemany("INSERT INTO promo_cards VALUES (?, ?, ?, ?, ?, ?, ?, ?)", new_promo_cards)

    con.commit()
    con.close()


def create_database(pokemon_list: list) -> None:
    con = sqlite3.connect("PokeDB.db")
    cur = con.cursor()
    cur.execute("DROP TABLE promo_cards")
    cur.execute("DROP TABLE normal_cards")
    cur.execute("CREATE TABLE normal_cards (id, name, set_num, num, pack, rarity, amount, stage)")
    cur.execute("CREATE TABLE promo_cards (id, name, set_num, num, pack, rarity, amount, stage)")

    normal_carads = json2db_data_parser([i for i in pokemon_list if i['id'][:2] != 'pa'])
    promo_cards = json2db_data_parser([i for i in pokemon_list if i['id'][:2] == 'pa'])

    cur.executemany("INSERT INTO normal_cards VALUES (?, ?, ?, ?, ?, ?, ?, ?)", normal_carads)
    cur.executemany("INSERT INTO promo_cards VALUES (?, ?, ?, ?, ?, ?, ?, ?)", promo_cards)
    con.commit()
    con.close()


def json2id_data_parser(json: list) -> list:
    procesed_cards = []
    for i, pokemon in enumerate(json):
        procesed_cards.append((i,))
    return procesed_cards


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
