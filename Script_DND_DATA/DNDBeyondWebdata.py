import requests
import re

class DnDBeyondCharacterService:
    @staticmethod
    def extract_character_id(url):
        match = re.search(r'characters/(\d+)', url)
        return match.group(1) if match else None

    @staticmethod
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
            return None

    @staticmethod
    def parse_character_data(data):
        if not data:
            return {"error": "Keine Daten gefunden."}
        
        character = data.get("data", {})
        modifiers = character.get("modifiers", {}).get("class", []) + \
                    character.get("modifiers", {}).get("race", []) + \
                    character.get("modifiers", {}).get("item", [])

        name = character.get("name", "Unbekannt")
        level = sum(cls.get("level", 0) for cls in character.get("classes", []))
        race = character.get("race", {}).get("fullName", "Unbekannt")
        background = character.get("background", {}).get("definition", {}).get("name", "Unbekannt")
        classes = ", ".join(f"{cls.get('definition', {}).get('name', 'Unbekannt')}" for cls in character.get("classes", []))
        subclass = ", ".join(f"{cls.get('subclassDefinition', {}).get('name', 'Unbekannt')}" for cls in character.get("classes", []))
        alignment = character.get("alignment", {}).get("name", "Unbekannt")
        conditions = ", ".join(character.get("conditions", []))
        update_link = f"https://www.dndbeyond.com/characters/{character.get('id', '')}"
        proficiency_bonus = character.get("modifiers", {}).get("proficiencyBonus", 2)
        speed = character.get("race", {}).get("speed", {}).get("walk", 30)
        gender = character.get("gender", "Unbekannt")
        death_save_success = character.get("deathSaves", {}).get("successes", 0)
        death_save_failure = character.get("deathSaves", {}).get("failures", 0)
        exhaustion = character.get("exhaustion", 0)
        initiative_adjustment = character.get("modifiers", {}).get("initiative", 0)
        proficiency_bonus_adjustment = character.get("modifiers", {}).get("proficiencyBonusAdjustment", 0)

        # Attribute
        stat_names = {
            1: "strength",
            2: "dexterity",
            3: "constitution",
            4: "intelligence",
            5: "wisdom",
            6: "charisma"
        }
        attributes = []
        for stat in character.get("stats", []):
            stat_id = stat.get("id") or stat.get("statId")
            value = stat.get("value")
            if stat_id is not None and value is not None:
                attribute_name = stat_names.get(stat_id, "Unbekannt")
                attributes.append({
                    "attribute_name": attribute_name,
                    "attribute_value": value,
                    "attribute_adjustment": 0  # Kann angepasst werden, falls nötig
                })

        # AC
        ac_base = character.get("armorClass", 10)
        ac_modified = character.get("modifiers", {}).get("armorClass", 0)
        ac = [{
            "ac_base": ac_base,
            "ac_modified": ac_modified
        }]

        # Saving Throws
        saving_throws = []
        for stat_id, stat_name in stat_names.items():
            is_proficient = any(
                modifier.get("type") == "proficiency" and
                modifier.get("subType") == f"saves-{stat_name}"
                for modifier in modifiers
            )
            saving_throws.append({
                "saving_throw_name": stat_name,
                "saving_throw_adjustment": 0,  # Kann angepasst werden, falls nötig
                "saving_throw_is_proficient": is_proficient
            })

        # Skills
        skill_names = {
            "athletics": "strength",
            "acrobatics": "dexterity",
            "animal_handling": "wisdom",
            "arcana": "intelligence",
            "deception": "charisma",
            "history": "intelligence",
            "insight": "wisdom",
            "intimidation": "charisma",
            "investigation": "intelligence",
            "medicine": "wisdom",
            "nature": "intelligence",
            "perception": "wisdom",
            "performance": "charisma",
            "persuasion": "charisma",
            "religion": "intelligence",
            "sleight_of_hand": "dexterity",
            "stealth": "dexterity",
            "survival": "wisdom"
        }
        skills = []
        for skill_name, ability in skill_names.items():
            is_proficient = any(
                modifier.get("type") == "proficiency" and
                modifier.get("subType") == f"skills-{skill_name}"
                for modifier in modifiers
            )
            is_expertise = any(
                modifier.get("type") == "expertise" and
                modifier.get("subType") == f"skills-{skill_name}"
                for modifier in modifiers
            )
            skills.append({
                "skill_name": skill_name,
                "skill_adjustment": 0,  # Kann angepasst werden, falls nötig
                "skill_is_proficient": is_proficient,
                "skill_is_expertise": is_expertise
            })

        # Hit Points
        hit_points = [{
            "hit_points_current": character.get("currentHp", 30),
            "hit_points_max": character.get("maxHp", 30),
            "hit_points_temp": character.get("tempHp", 0),
            "non_lethal_damage": 0  # Kann angepasst werden, falls nötig
        }]

        # JSON-Struktur
        return {
            "stats": [{
                "character_is_inspired": False,  # Kann angepasst werden, falls nötig
                "character_name": name,
                "character_class": classes,
                "character_race": race,
                "character_background": background,
                "character_subclass": subclass,
                "character_level": level,
                "character_alignment": alignment,
                "character_conditions": conditions,
                "character_update_link": update_link,
                "character_proficiency_bonus": proficiency_bonus,
                "character_speed": speed,
                "character_gender": gender,
                "character_death_save_success": death_save_success,
                "character_death_save_failure": death_save_failure,
                "character_exhaustion": exhaustion,
                "character_initiative_adjustment": initiative_adjustment,
                "character_proficiency_bonus_adjustment": proficiency_bonus_adjustment
            }],
            "attributes": attributes,
            "ac": ac,
            "saving_throw_proficiencies": saving_throws,
            "skills": skills,
            "hit_points": hit_points
        }

    def get_character_info(self, url):
        character_id = self.extract_character_id(url)
        if not character_id:
            return {"error": "Ungültige URL oder Charakter-ID nicht gefunden."}
        
        char_data = self.fetch_character_data(character_id)
        if not char_data:
            return {"error": "Charakterdaten konnten nicht abgerufen werden."}
        
        return self.parse_character_data(char_data)


# Hauptprogramm
if __name__ == "__main__":
    service = DnDBeyondCharacterService()
    dnd_beyond_url = input("Gib den D&D Beyond Charakterlink ein: ")
    character_info = service.get_character_info(dnd_beyond_url)
    
    if "error" in character_info:
        print(character_info["error"])
    else:
        import json
        print(json.dumps(character_info, indent=4))