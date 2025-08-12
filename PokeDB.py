import sqlite3
import json

with open('pokemon_list.json', 'r', encoding='utf-8') as f:
    raw_pokemon_list = json.load(f)


def main() -> None:
    pokemon_list = change_rarity(raw_pokemon_list)
    create_database(pokemon_list=pokemon_list)


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
        'Promo': 'promo'}

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
    cur.execute("DROP TABLE POKEMONS")
    cur.execute("CREATE TABLE POKEMONS (card_id, name, pack, rarity, amount, stage)")
    data = []
    for pokemon in pokemon_list:
        pokemon_data = (
            pokemon['id'],
            pokemon['name'],
            pokemon['pack'],
            pokemon['rarity'],
            None,
            None
        )
        data.append(pokemon_data)
    cur.executemany("INSERT INTO POKEMONS VALUES (?, ?, ?, ?, ?, ?)", data)
    con.commit()


if __name__ == '__main__':
    main()