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
    def calculate_skill_or_save_value(attribute_modifier, proficiency_bonus, is_proficient, is_expertise):
        value = attribute_modifier
        if is_proficient:
            value += proficiency_bonus
        if is_expertise:
            value += proficiency_bonus  # Expertise doubles the proficiency bonus
        return value

    @staticmethod
    def print_modifiers(modifiers):
        print("Modifiers:")
        for modifier in modifiers:
            print(f"- Type: {modifier.get('type', 'Unknown')}")
            print(f"  Subtype: {modifier.get('subType', 'Unknown')}")
            print(f"  Value: {modifier.get('value', 'No Value')}")
            print(f"  Source: {modifier.get('entityType', 'Unknown')}")
            print(f"  ID: {modifier.get('id', 'No ID')}")
            print(f"  Description: {modifier.get('friendlySubtypeName', 'No Description')}")
            print()

    @staticmethod
    def parse_character_data(data):
        if not data:
            return {"error": "No data found."}
        
        character = data.get("data", {})
        
        # Collect modifiers from all relevant sources
        modifiers = []
        for modifier_type in ["race", "feats", "magic-items", "class", "background"]:
            modifiers.extend(character.get("modifiers", {}).get(modifier_type, []))

        # Debugging: Print modifiers
        #DnDBeyondCharacterService.print_modifiers(modifiers)

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
        initiative_adjustment = character.get("modifiers", {}).get("initiative", 0)
        proficiency_bonus_adjustment = character.get("modifiers", {}).get("proficiencyBonusAdjustment", 0)

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
        for stat in character.get("stats", []):
            stat_id = stat.get("id") or stat.get("statId")
            base_value = stat.get("value")
            if stat_id is not None and base_value is not None:
                attribute_name = stat_names.get(stat_id, "Unknown")
                total_value = DnDBeyondCharacterService.calculate_attribute_value(base_value, modifiers, stat_id, attribute_name)
                attributes.append({
                    "attribute_name": attribute_name,
                    "attribute_value": total_value,
                    "attribute_modifier": (total_value - 10) // 2  # Calculate modifier
                })

        # Debugging: Print calculated attributes
        #print("Calculated Attributes:", attributes)

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
            attribute_modifier = 0
            for attribute in attributes:
                if attribute["attribute_name"] == ability:
                    attribute_modifier = attribute["attribute_modifier"]
                    break
            
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
                "skill_adjustment": skill_value,
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
            attribute_modifier = 0
            for attribute in attributes:
                if attribute["attribute_name"] == stat_name:
                    attribute_modifier = attribute["attribute_modifier"]
                    break
            
            # Check if the character is proficient in the saving throw
            is_proficient = any(
                modifier.get("type") == "proficiency" and
                (
                    f"{stat_name}-saving-throws" in modifier.get("subType", "").lower() or  # Check for stat name
                    f"{stat_id}-saving-throws" in modifier.get("subType", "").lower()      # Check for stat ID
                )
                for modifier in modifiers
            )
            
            # Debugging: Print modifiers related to saving throws
            print(f"Checking saving throw: {stat_name} (ID: {stat_id})")
            for modifier in modifiers:
                if modifier.get("type") == "proficiency" and "saving-throws" in modifier.get("subType", "").lower():
                    print(f"Modifier: {modifier.get('subType')}, Value: {modifier.get('value')}")
            
            # Calculate the saving throw value
            saving_throw_value = DnDBeyondCharacterService.calculate_skill_or_save_value(
                attribute_modifier, proficiency_bonus, is_proficient, False  # Expertise does not apply to saving throws
            )
            
            saving_throws.append({
                "saving_throw_name": stat_name,
                "saving_throw_adjustment": saving_throw_value,
                "saving_throw_is_proficient": is_proficient
            })

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
                "character_initiative_adjustment": initiative_adjustment,
                "character_proficiency_bonus_adjustment": proficiency_bonus_adjustment
            }],
            "attributes": attributes,
            "skills": skills,
            "saving_throws": saving_throws
        }

    def get_character_info(self, url):
        character_id = self.extract_character_id(url)
        if not character_id:
            return {"error": "Invalid URL or character ID not found."}
        
        char_data = self.fetch_character_data(character_id)
        if not char_data:
            return {"error": "Character data could not be retrieved."}
        
        # Debugging: Print the entire character data
        import json
        print(json.dumps(char_data, indent=4))
        
        return self.parse_character_data(char_data)


# Main program
if __name__ == "__main__":
    service = DnDBeyondCharacterService()
    dnd_beyond_url = input("Enter the D&D Beyond character URL: ")
    character_info = service.get_character_info(dnd_beyond_url)
    
    if "error" in character_info:
        print(character_info["error"])
    else:
        import json
        print(json.dumps(character_info, indent=4))