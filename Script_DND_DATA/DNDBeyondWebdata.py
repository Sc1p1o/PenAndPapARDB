import requests
import json
import re

def extract_character_id(url):
    match = re.search(r'characters/(\d+)', url)
    return match.group(1) if match else None

def fetch_character_data(character_id):
    api_url = f'https://character-service.dndbeyond.com/character/v5/character/{character_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Fehler: {response.status_code}")
        return None

def parse_character_data(data):
    if not data:
        return "Keine Daten gefunden."
    
    character = data.get("data", {})
    name = character.get("name", "Unbekannt")
    level = sum(cls.get("level", 0) for cls in character.get("classes", []))
    race = character.get("race", {}).get("fullName", "Unbekannt")
    background = character.get("background", {}).get("definition", {}).get("name", "Unbekannt")
    
    classes = ", ".join(f"{cls.get('definition', {}).get('name', 'Unbekannt')} (Level {cls.get('level', 0)})" for cls in character.get("classes", []))
    
    stat_names = {1: "Stärke", 2: "Geschicklichkeit", 3: "Konstitution", 4: "Intelligenz", 5: "Weisheit", 6: "Charisma"}
    stats = {}
    for stat in character.get("stats", []):
        stat_id = stat.get("id") or stat.get("statId")
        value = stat.get("value")
        if stat_id is not None and value is not None:
            stats[stat_id] = value
    
    stats_formatted = "\n".join(f"{stat_names.get(k, 'Unbekannt')}: {v}" for k, v in stats.items())
    
    equipment = "\n".join(f"{item.get('definition', {}).get('name', 'Unbekannt')} (Menge: {item.get('quantity', 1)})" for item in character.get("inventory", []))
    
    currency = character.get("currencies", {})
    gold = currency.get("gp", 0)
    silver = currency.get("sp", 0)
    copper = currency.get("cp", 0)
    electrum = currency.get("ep", 0)
    platinum = currency.get("pp", 0)
    currency_formatted = f"Platin: {platinum}\nGold: {gold}\nSilber: {silver}\nKupfer: {copper}\nElectrum: {electrum}"
    
    return f"Name: {name}\nLevel: {level}\nRasse: {race}\nHintergrund: {background}\nKlassen: {classes}\n\nAttribute:\n{stats_formatted}\n\nAusrüstung:\n{equipment}\n\nWährung:\n{currency_formatted}"

if __name__ == "__main__":
    dnd_beyond_url = input("Gib den D&D Beyond Charakterlink ein: ")
    character_id = extract_character_id(dnd_beyond_url)
    
    if character_id:
        char_data = fetch_character_data(character_id)
        print(parse_character_data(char_data))
    else:
        print("Ungültige URL oder Charakter-ID nicht gefunden.")
