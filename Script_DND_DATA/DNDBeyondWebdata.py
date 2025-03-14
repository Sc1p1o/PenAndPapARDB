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
    def map_condition_id_to_name(condition_id):
        condition_mapping = {
            1: "Blinded",
            2: "Charmed",
            3: "Deafened",
            4: "Frightened",
            5: "Grappled",
            6: "Incapacitated",
            7: "Invisible",
            8: "Paralyzed",
            9: "Petrified",
            10: "Poisoned",
            11: "Prone",
            12: "Restrained",
            13: "Stunned",
            14: "Unconscious",
            15: "Exhaustion"
        }
        return condition_mapping.get(condition_id, "Unbekannte Bedingung")

    @staticmethod
    def map_alignment_id_to_name(alignment_id):
        alignment_mapping = {
            1: "Lawful Good",
            2: "Neutral Good",
            3: "Chaotic Good",
            4: "Lawful Neutral",
            5: "Neutral",
            6: "Chaotic Neutral",
            7: "Lawful Evil",
            8: "Neutral Evil",
            9: "Chaotic Evil"
        }
        return alignment_mapping.get(alignment_id, "Unbekannt")

    @staticmethod
    def calculate_proficiency_bonus(level):
        if level < 1:
            return 0
        elif level <= 4:
            return 2
        elif level <= 8:
            return 3
        elif level <= 12:
            return 4
        elif level <= 16:
            return 5
        else:
            return 6

    @staticmethod
    def calculate_attribute_value(base_value, modifiers, stat_id, stat_name):
        modifier_value = sum(
            modifier.get("value", 0)
            for modifier in modifiers
            if (
                modifier.get("subType", "").endswith(f"stats-{stat_id}") or
                modifier.get("subType", "").endswith(f"{stat_name}-score") or
                modifier.get("subType", "").endswith(f"{stat_name}-modifier")
            )
        )
        return base_value + modifier_value

    @staticmethod
    def calculate_speed(base_speed, modifiers):
        speed_modifiers = 0
        for modifier in modifiers:
            if (
                "speed" in modifier.get("subType", "").lower() or
                modifier.get("type") == "bonus" and "speed" in modifier.get("friendlySubtypeName", "").lower()
            ):
                value = modifier.get("value", 0)
                if value is not None:
                    speed_modifiers += value
        return base_speed + speed_modifiers

    @staticmethod
    def calculate_skill_value(attribute_modifier, proficiency_bonus, is_proficient, is_expertise):
        skill_value = attribute_modifier
        if is_proficient:
            skill_value += proficiency_bonus
        if is_expertise:
            skill_value += proficiency_bonus  # Expertise verdoppelt den Proficiency-Bonus
        return skill_value

    @staticmethod
    def print_modifiers(modifiers):
        print("Modifikatoren:")
        for modifier in modifiers:
            print(f"- Typ: {modifier.get('type', 'Unbekannt')}")
            print(f"  Subtyp: {modifier.get('subType', 'Unbekannt')}")
            print(f"  Wert: {modifier.get('value', 'Kein Wert')}")
            print(f"  Quelle: {modifier.get('entityType', 'Unbekannt')}")
            print(f"  ID: {modifier.get('id', 'Keine ID')}")
            print(f"  Beschreibung: {modifier.get('friendlySubtypeName', 'Keine Beschreibung')}")
            print()

    @staticmethod
    def parse_character_data(data):
        if not data:
            return {"error": "Keine Daten gefunden."}
        
        character = data.get("data", {})
        
        # Sammle Modifikatoren aus allen relevanten Quellen
        modifiers = []
        for modifier_type in ["race", "feats", "magic-items", "class", "background"]:
            modifiers.extend(character.get("modifiers", {}).get(modifier_type, []))

        # Debugging: Gib die Modifikatoren aus
        DnDBeyondCharacterService.print_modifiers(modifiers)

        # Charakterlevel berechnen
        level = sum(cls.get("level", 0) for cls in character.get("classes", []))
        
        # Proficiency-Bonus basierend auf dem Level berechnen
        proficiency_bonus = DnDBeyondCharacterService.calculate_proficiency_bonus(level)

        # Basisgeschwindigkeit (z. B. 30 Fuß für die meisten Rassen)
        base_speed = character.get("race", {}).get("speed", {}).get("walk", 30)
        
        # Geschwindigkeit unter Berücksichtigung von Modifikatoren berechnen
        speed = DnDBeyondCharacterService.calculate_speed(base_speed, modifiers)

        # Allgemeine Charakterdaten
        name = character.get("name", "Unbekannt")
        race = character.get("race", {}).get("fullName", "Unbekannt")
        background = character.get("background", {}).get("definition", {}).get("name", "Unbekannt") if character.get("background") else "Unbekannt"
        classes = ", ".join(f"{cls.get('definition', {}).get('name', 'Unbekannt')}" for cls in character.get("classes", []))
        subclass = ", ".join(f"{cls.get('subclassDefinition', {}).get('name', 'Unbekannt')}" for cls in character.get("classes", []))
        
        # Alignment
        alignment_id = character.get("alignmentId")
        alignment = DnDBeyondCharacterService.map_alignment_id_to_name(alignment_id)

        # Verarbeitung der conditions
        conditions = []
        for cond in character.get("conditions", []):
            if isinstance(cond, dict):
                condition_id = cond.get("id")
                condition_name = DnDBeyondCharacterService.map_condition_id_to_name(condition_id)
                if condition_id == 15:  # Exhaustion
                    exhaustion_level = cond.get("level", 0)  # Extrahiere das Exhaustion-Level
                    conditions.append(f"{condition_name} (Level {exhaustion_level})")
                else:
                    conditions.append(condition_name)
            elif isinstance(cond, int):
                condition_name = DnDBeyondCharacterService.map_condition_id_to_name(cond)
                conditions.append(condition_name)
        
        conditions_str = ", ".join(conditions) if conditions else "Keine"

        update_link = f"https://www.dndbeyond.com/characters/{character.get('id', '')}"
        gender = character.get("gender", "Unbekannt")
        death_save_success = character.get("deathSaves", {}).get("successes", 0)
        death_save_failure = character.get("deathSaves", {}).get("failures", 0)
        exhaustion = character.get("exhaustion", 0)  # Extrahiere das Exhaustion-Level
        initiative_adjustment = character.get("modifiers", {}).get("initiative", 0)
        proficiency_bonus_adjustment = character.get("modifiers", {}).get("proficiencyBonusAdjustment", 0)

        # Inspiration
        is_inspired = character.get("inspiration", False)  # Extrahiere das Inspiration-Flag

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
            base_value = stat.get("value")
            if stat_id is not None and base_value is not None:
                attribute_name = stat_names.get(stat_id, "Unbekannt")
                total_value = DnDBeyondCharacterService.calculate_attribute_value(base_value, modifiers, stat_id, attribute_name)
                attributes.append({
                    "attribute_name": attribute_name,
                    "attribute_value": total_value,
                    "attribute_adjustment": 0  # Kann angepasst werden, falls nötig
                })

        # Debugging: Gib die berechneten Attributwerte aus
        print("Berechnete Attribute:", attributes)

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
            # Finde den Attributsmodifikator für den Rettungswurf
            attribute_modifier = 0
            for attribute in attributes:
                if attribute["attribute_name"] == stat_name:
                    attribute_modifier = (attribute["attribute_value"] - 10) // 2  # Berechne den Modifikator
                    break
            
            # Überprüfe, ob der Charakter in diesem Rettungswurf proficient ist
            is_proficient = any(
                modifier.get("type") == "proficiency" and
                modifier.get("subType") == f"saves-{stat_name}"
                for modifier in modifiers
            )
            
            # Berechne den Rettungswurf-Wert
            saving_throw_value = attribute_modifier
            if is_proficient:
                saving_throw_value += proficiency_bonus
            
            saving_throws.append({
                "saving_throw_name": stat_name,
                "saving_throw_adjustment": saving_throw_value,
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
            # Finde den Attributsmodifikator für den Skill
            attribute_modifier = 0
            for attribute in attributes:
                if attribute["attribute_name"] == ability:
                    attribute_modifier = (attribute["attribute_value"] - 10) // 2  # Berechne den Modifikator
                    break
            
            # Überprüfe, ob der Charakter in diesem Skill proficient ist
            is_proficient = any(
                modifier.get("type") == "proficiency" and
                modifier.get("subType") == f"skills-{skill_name}"
                for modifier in modifiers
            )
            
            # Überprüfe, ob der Charakter in diesem Skill Expertise hat
            is_expertise = any(
                modifier.get("type") == "expertise" and
                modifier.get("subType") == f"skills-{skill_name}"
                for modifier in modifiers
            )
            
            # Berechne den Skill-Wert
            skill_value = DnDBeyondCharacterService.calculate_skill_value(
                attribute_modifier, proficiency_bonus, is_proficient, is_expertise
            )
            
            skills.append({
                "skill_name": skill_name,
                "skill_adjustment": skill_value,
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
                "character_is_inspired": is_inspired,  # Inspiration-Flag
                "character_name": name,
                "character_class": classes,
                "character_race": race,
                "character_background": background,
                "character_subclass": subclass,
                "character_level": level,
                "character_alignment": alignment,
                "character_conditions": conditions_str,
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
        
        # Debugging: Gib die gesamten Charakterdaten aus
        import json
        print(json.dumps(char_data, indent=4))
        
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