import requests
import re
import json

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
        return condition_mapping.get(condition_id, "Unknown Condition")

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
        return alignment_mapping.get(alignment_id, "Unknown")

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
        # Set all adjustments to 0
        return base_value

    @staticmethod
    def calculate_speed(base_speed, modifiers):
        # Set all adjustments to 0
        return base_speed

    @staticmethod
    def calculate_skill_or_save_value(attribute_modifier, proficiency_bonus, is_proficient, is_expertise):
        # Set all adjustments to 0
        return 0

    @staticmethod
    def parse_character_data(data):
        if not data:
            return {"error": "No data found."}
        
        character = data.get("data", {})
        
        # Collect modifiers from all relevant sources
        modifiers = []
        for modifier_type in ["race", "feats", "magic-items", "class", "background"]:
            modifiers.extend(character.get("modifiers", {}).get(modifier_type, []))

        # Calculate character level
        level = sum(cls.get("level", 0) for cls in character.get("classes", []))
        
        # Calculate proficiency bonus based on level
        proficiency_bonus = DnDBeyondCharacterService.calculate_proficiency_bonus(level)

        # Base speed (e.g., 30 feet for most races)
        base_speed = character.get("race", {}).get("speed", {}).get("walk", 30)
        
        # Calculate speed with modifiers
        speed = DnDBeyondCharacterService.calculate_speed(base_speed, modifiers)

        # General character data
        name = character.get("name", "Unknown")
        race = character.get("race", {}).get("fullName", "Unknown")
        background = character.get("background", {}).get("definition", {}).get("name", "Unknown") if character.get("background") else "Unknown"
        classes = ", ".join(f"{cls.get('definition', {}).get('name', 'Unknown')}" for cls in character.get("classes", []))
        subclass = ", ".join(f"{cls.get('subclassDefinition', {}).get('name', 'Unknown')}" for cls in character.get("classes", []))
        
        # Alignment
        alignment_id = character.get("alignmentId")
        alignment = DnDBeyondCharacterService.map_alignment_id_to_name(alignment_id)

        # Process conditions
        conditions = []
        for cond in character.get("conditions", []):
            if isinstance(cond, dict):
                condition_id = cond.get("id")
                condition_name = DnDBeyondCharacterService.map_condition_id_to_name(condition_id)
                if condition_id == 15:  # Exhaustion
                    exhaustion_level = cond.get("level", 0)  # Extract exhaustion level
                    conditions.append(f"{condition_name} (Level {exhaustion_level})")
                else:
                    conditions.append(condition_name)
            elif isinstance(cond, int):
                condition_name = DnDBeyondCharacterService.map_condition_id_to_name(cond)
                conditions.append(condition_name)
        
        conditions_str = ", ".join(conditions) if conditions else "None"

        update_link = f"https://www.dndbeyond.com/characters/{character.get('id', '')}"
        gender = character.get("gender", "Unknown")
        death_save_success = character.get("deathSaves", {}).get("successes", 0)
        death_save_failure = character.get("deathSaves", {}).get("failures", 0)
        exhaustion = character.get("exhaustion", 0)  # Extract exhaustion level
        initiative_adjustment = 0  # Set to 0
        proficiency_bonus_adjustment = 0  # Set to 0

        # Inspiration
        is_inspired = character.get("inspiration", False)

        # Attributes
        stat_names = {
            1: "strength",
            2: "dexterity",
            3: "constitution",
            4: "intelligence",
            5: "wisdom",
            6: "charisma"
        }
        attributes = []
        for stat_id, stat_name in stat_names.items():
            stat = next((s for s in character.get("stats", []) if s.get("id") == stat_id or s.get("statId") == stat_id), None)
            base_value = stat.get("value", 10) if stat else 10
            total_value = DnDBeyondCharacterService.calculate_attribute_value(base_value, modifiers, stat_id, stat_name)
            attributes.append({
                "attribute_name": stat_name,
                "attribute_value": total_value,
                "attribute_adjustment": 0  # Set to 0
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
            # Find the attribute modifier for the skill
            attribute_modifier = next((attr["attribute_adjustment"] for attr in attributes if attr["attribute_name"] == ability), 0)
            
            # Check if the character is proficient in the skill
            is_proficient = any(
                modifier.get("type") == "proficiency" and
                skill_name in modifier.get("subType", "").lower()  # Check if skill_name is in subType
                for modifier in modifiers
            )
            
            # Check if the character has expertise in the skill
            is_expertise = any(
                modifier.get("type") == "expertise" and
                skill_name in modifier.get("subType", "").lower()  # Check if skill_name is in subType
                for modifier in modifiers
            )
            
            # Calculate the skill value
            skill_value = DnDBeyondCharacterService.calculate_skill_or_save_value(
                attribute_modifier, proficiency_bonus, is_proficient, is_expertise
            )
            
            skills.append({
                "skill_name": skill_name,
                "skill_adjustment": 0,  # Set to 0
                "skill_is_proficient": is_proficient,
                "skill_is_expertise": is_expertise
            })

        # Saving Throws
        saving_throw_names = {
            1: "strength",
            2: "dexterity",
            3: "constitution",
            4: "intelligence",
            5: "wisdom",
            6: "charisma"
        }
        saving_throws = []
        for stat_id, stat_name in saving_throw_names.items():
            # Find the attribute modifier for the saving throw
            attribute_modifier = next((attr["attribute_adjustment"] for attr in attributes if attr["attribute_name"] == stat_name), 0)
            
            # Check if the character is proficient in the saving throw
            is_proficient = any(
                modifier.get("type") == "proficiency" and
                (
                    f"{stat_name}-saving-throws" in modifier.get("subType", "").lower() or  # Check for stat name
                    f"{stat_id}-saving-throws" in modifier.get("subType", "").lower()      # Check for stat ID
                )
                for modifier in modifiers
            )
            
            # Calculate the saving throw value
            saving_throw_value = DnDBeyondCharacterService.calculate_skill_or_save_value(
                attribute_modifier, proficiency_bonus, is_proficient, False  # Expertise does not apply to saving throws
            )
            
            saving_throws.append({
                "saving_throw_name": stat_name,
                "saving_throw_adjustment": 0,  # Set to 0
                "saving_throw_is_proficient": is_proficient
            })

        # Hit Points
        hit_points = [{
            "hit_points_current": character.get("currentHp", 0),
            "hit_points_max": character.get("maxHp", 0),
            "hit_points_temp": character.get("tempHp", 0),
            "non_lethal_damage": 0  # Not directly available in D&D Beyond data
        }]

        # Armor Class (AC)
        ac = [{
            "ac_base": character.get("armorClass", 10),
            "ac_modified": 0  # Set to 0
        }]

        # JSON structure
        return {
            "stats": [{
                "character_is_inspired": is_inspired,
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
                "character_initiative_adjustment": 0,  # Set to 0
                "character_proficiency_bonus_adjustment": 0  # Set to 0
            }],
            "attributes": attributes,
            "skills": skills,
            "saving_throw_proficiencies": saving_throws,
            "hit_points": hit_points,
            "ac": ac
        }

    def get_character_info(self, url):
        character_id = self.extract_character_id(url)
        if not character_id:
            return {"error": "Invalid URL or character ID not found."}
        
        char_data = self.fetch_character_data(character_id)
        if not char_data:
            return {"error": "Character data could not be retrieved."}
        
        return self.parse_character_data(char_data)


class DjangoDBService:
    def __init__(self, api_url):
        self.api_url = api_url

    def send_character_data(self, character_data):
        """
        Sendet die Charakterdaten als POST-Anfrage an die Django-Datenbank.
        
        :param character_data: Die Charakterdaten, die gesendet werden sollen.
        :return: Die Antwort der Django-API.
        """
        headers = {
            'Content-Type': 'application/json',
        }
        
        try:
            response = requests.post(self.api_url, data=json.dumps(character_data), headers=headers)
            response.raise_for_status()  # Wirft eine Ausnahme bei einem Fehlerstatuscode
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Fehler beim Senden der Daten an die Django-Datenbank: {e}"}


# Main program
if __name__ == "__main__":
    # Instanz der DnDBeyondCharacterService-Klasse erstellen
    service = DnDBeyondCharacterService()
    dnd_beyond_url = input("Enter the D&D Beyond character URL: ")
    character_info = service.get_character_info(dnd_beyond_url)
    
    if "error" in character_info:
        print(character_info["error"])
    else:
        # Instanz der DjangoDBService-Klasse erstellen
        django_api_url = "http://127.0.0.1:8000/api/stats/"
        db_service = DjangoDBService(django_api_url)
        
        # Daten an die Django-Datenbank senden
        result = db_service.send_character_data(character_info)
        print(result)