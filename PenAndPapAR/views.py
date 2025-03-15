from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from PenAndPapAR.ViewsHelper.DNDBeyondWebdata import DnDBeyondCharacterService
from PenAndPapAR.models import Attributes, CharacterStats, AC, SavingThrowProficiencies, Skills, HitPoints
from PenAndPapAR.serializers import (
    CharacterStatsSerializer,
    AttributesSerializer,
    ACSerializer,
    SavingThrowProficienciesSerializer,
    SkillsSerializer,
    HitPointsSerializer
)

# Templates für Standardwerte
character_stats_template = {
    "character_is_inspired": False,
    "character_name": None,
    "character_class": None,
    "character_race": None,
    "character_background": None,
    "character_subclass": None,
    "character_level": 1,
    "character_alignment": None,
    "character_conditions": None,
    "character_source_link": None,
    "character_proficiency_bonus": 2,

    "character_speed": 30,
    "character_gender": None,
    "character_death_save_success": None,
    "character_death_save_failure": None,
    "character_exhaustion": None,
    "character_initiative_adjustment": None,
    "character_proficiency_bonus_adjustment": 0
}

attribute_template = {
    "attribute_name": "strength",
    "attribute_value": 10,
    "attribute_adjustment": 0
}

ac_template = {
    "ac_base": 10,
    "ac_modified": 0
}

saving_throw_proficiencies_template = {
    "saving_throw_name": "strength",
    "saving_throw_adjustment": 0,
    "saving_throw_is_proficient": False}

skills_template = {
    "skill_name": "athletics",
    "skill_adjustment": 0,
    "skill_is_proficient": False,
    "skill_is_expertise": False
}

hit_points_template = {
    "hit_points_current": 30,
    "hit_points_max": 30,
    "hit_points_temp": 0,
    "non_lethal_damage": 0
}


templates = [
    character_stats_template,
    attribute_template,
    ac_template,
    saving_throw_proficiencies_template,
    skills_template,
    hit_points_template
]


class CharacterStatsView(APIView):
    def get(self, request, *args, **kwargs):
        print("GET Request Arrived")
        character_id = request.GET.get('character_id', "#0000")


        character_stats = CharacterStats.objects.filter(character_id=character_id)
        character_attributes = Attributes.objects.filter(attribute_character=character_id)
        character_ac = AC.objects.filter(ac_character=character_id)
        character_saving_throw_proficiencies = SavingThrowProficiencies.objects.filter(
            saving_throw_proficiency_character=character_id)
        character_skills = Skills.objects.filter(skill_character=character_id)
        character_hit_points = HitPoints.objects.filter(hit_points_character=character_id)

        stats_serializer = CharacterStatsSerializer(character_stats, many=True)
        attributes_serializer = AttributesSerializer(character_attributes, many=True)
        ac_serializer = ACSerializer(character_ac, many=True)
        saving_throw_proficiencies_serializer = SavingThrowProficienciesSerializer(
            character_saving_throw_proficiencies, many=True)
        skills_serializer = SkillsSerializer(character_skills, many=True)
        hit_points_serializer = HitPointsSerializer(character_hit_points, many=True)

        serializer_set = [stats_serializer,
                          attributes_serializer,
                          ac_serializer,
                          saving_throw_proficiencies_serializer,
                          skills_serializer,
                          hit_points_serializer]

        return Response(
            {
                "stats": stats_serializer.data,
                "attributes": attributes_serializer.data,
                "ac": ac_serializer.data,
                "saving_throw_proficiencies": saving_throw_proficiencies_serializer.data,
                "skills": skills_serializer.data,
                "hit_points": hit_points_serializer.data,
            }, status=status.HTTP_200_OK)

    def post(self, request):
        # prepare lists
        skill_name_list = [
            "acrobatics",
            "animal_handling",
            "arcana",
            "athletics",
            "deception",
            "history",
            "insight",
            "intimidation",
            "investigation",
            "medicine",
            "nature",
            "perception",
            "performance",
            "persuasion",
            "religion",
            "sleight_of_hand",
            "stealth",
            "survival"
        ]
        topics = ["stats", "attributes", "ac", "saving_throw_proficiencies", "skills", "hit_points",]
        attribute_name_list = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        saving_throw_name_list = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]

        # prepare and validate data from request
        data = request.data


        # test if link is not empty
        if data["stats"][0]["character_source_link"] == "" or data["stats"][0]["character_source_link"] is None:
            url = ""
        else:
            url = data["stats"][0]["character_source_link"]
            
            service = DnDBeyondCharacterService()
            character_info = service.get_character_info(url)


            if "error" in character_info:
             return Response({"error": character_info["error"]}, status=status.HTTP_400_BAD_REQUEST)
            
            data = character_info
            #data = jkerz_char_json

        attributes_data = data.get("attributes")
        saving_throw_proficiencies_data = data.get("saving_throw_proficiencies")
        skills_data = data.get("skills")
        
        invalid_topic = validate_post_request(topics, data)

        if(invalid_topic is not None):
            return Response({"error": f"Missing data for topic '{invalid_topic}'."},
                            status=status.HTTP_400_BAD_REQUEST)


        # generate missing Traits
        attributes_data.extend(generate_character_trait(attribute_name_list, attributes_data, "attribute"))
        saving_throw_proficiencies_data.extend(generate_character_trait(saving_throw_name_list,
                                                                        saving_throw_proficiencies_data,
                                                                        "saving_throw"))
        skills_data.extend(generate_character_trait(skill_name_list, skills_data, "skill"))

        # generate and add Character ID to connect relations between tables
        generated_id = generate_character_id()
        data["stats"][0]["character_id"] = generated_id
        data["ac"][0]["ac_character"] = generated_id
        data["hit_points"][0]["hit_points_character"] = generated_id

        data_list = [attributes_data, saving_throw_proficiencies_data, skills_data]
        foreign_key_list = ["attribute_character", "saving_throw_proficiency_character", "skill_character"]

        for datas in data_list:
            for json_element in datas:
                json_element.update({foreign_key_list[data_list.index(datas)]: generated_id})
        # initialize serializers
        stats_serializer = CharacterStatsSerializer(data=data["stats"], many=True)
        attributes_serializer = AttributesSerializer(data=data["attributes"], many=True)
        ac_serializer = ACSerializer(data=data["ac"], many=True)
        saving_throw_proficiencies_serializer = SavingThrowProficienciesSerializer(data=data["saving_throw_proficiencies"],
                                                                               many=True)
        skills_serializer = SkillsSerializer(data=data["skills"], many=True)
        hit_points_serializer = HitPointsSerializer(data=data["hit_points"], many=True)

        serializer_set = [stats_serializer,
                          attributes_serializer,
                          ac_serializer,
                          saving_throw_proficiencies_serializer,
                          skills_serializer,
                          hit_points_serializer]

        # validate data with serializers and save valid data to db
        counter = 0
        for serializer in serializer_set:
            if serializer.is_valid():
                serializer.save()
            else:
                return Response({"error": f"Invalid data in character {topics[counter]}.\n"
                                          f"{serializer.errors}"},
                                status=status.HTTP_400_BAD_REQUEST)
            counter += 1

        return Response({"message": "Data has been successfully processed."}, status=status.HTTP_200_OK)


    def put(self, request):
        try:
            print("PUT Request Arrived")
            data = request.data
            stats_data = request.data.get("stats")
            attributes_data = request.data.get("attributes")
            saving_throw_proficiencies_data = request.data.get("saving_throw_proficiencies")
            ac_data = request.data.get("ac")
            skills_data = request.data.get("skills")
            hit_points_data = request.data.get("hit_points")

            character_id = stats_data[0]["character_id"]

            character_stats_db = CharacterStats.objects.filter(character_id=character_id)
            character_attributes_db = Attributes.objects.filter(attribute_character=character_id)
            character_ac_db = AC.objects.filter(ac_character=character_id)
            character_saving_throw_proficiencies_db = SavingThrowProficiencies.objects.filter(
                saving_throw_proficiency_character=character_id)
            character_skills_db = Skills.objects.filter(skill_character=character_id)
            character_hit_points_db = HitPoints.objects.filter(hit_points_character=character_id)

            if stats_data:
                for stat in stats_data:
                    character_stats_db.update(**stat)

            if attributes_data:
                for attr in attributes_data:
                    for attr_db in character_attributes_db:
                        if attr_db.attribute_name == attr["attribute_name"]:
                            if "attribute_value" in attr:
                                attr_db.attribute_value = attr["attribute_value"]
                            if "attribute_adjustment" in attr:
                                attr_db.attribute_adjustment = attr["attribute_adjustment"]

                            attr_db.save()
                            break

            if ac_data:
                for ac_trait in ac_data:
                    character_ac_db.update(**ac_trait)

            if saving_throw_proficiencies_data:
                for saving_throw_proficiency in saving_throw_proficiencies_data:
                    for saving_throw_proficiency_db in character_saving_throw_proficiencies_db:
                        if saving_throw_proficiency_db.saving_throw_name == saving_throw_proficiency["saving_throw_name"]:
                            if "saving_throw_adjustment" in saving_throw_proficiency:
                                saving_throw_proficiency_db.saving_throw_adjustment = saving_throw_proficiency[
                                    "saving_throw_adjustment"]
                            if "saving_throw_is_proficient" in saving_throw_proficiency:
                                saving_throw_proficiency_db.saving_throw_is_proficient = saving_throw_proficiency[
                                    "saving_throw_is_proficient"]
                            saving_throw_proficiency_db.save()
                            break
            if skills_data:
                for skill in skills_data:
                    for skill_db in character_skills_db:
                        if skill_db.skill_name == skill["skill_name"]:
                            if "skill_adjustment" in skill:
                                skill_db.skill_adjustment = skill["skill_adjustment"]
                            if "skill_is_proficient" in skill:
                                skill_db.skill_is_proficient = skill["skill_is_proficient"]
                            if "skill_is_expertise" in skill:
                                skill_db.skill_is_expertise = skill["skill_is_expertise"]
                            skill_db.save()
                            break

            if hit_points_data:
                for hit_point_trait in hit_points_data:
                    character_hit_points_db.update(**hit_point_trait)

            return Response({
                "stats": CharacterStatsSerializer(character_stats_db, many=True).data,
                "attributes": AttributesSerializer(character_attributes_db, many=True).data,
                "ac": ACSerializer(character_ac_db, many=True).data,
                "saving_throw_proficiencies": SavingThrowProficienciesSerializer(character_saving_throw_proficiencies_db,
                                                                                 many=True).data,
                "skills": SkillsSerializer(character_skills_db, many=True).data,
                "hit_points": HitPointsSerializer(character_hit_points_db, many=True).data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_400_BAD_REQUEST)

def generate_character_id():
    existing_ids = CharacterStats.objects.values_list('character_id', flat=True).order_by('character_id')
    min_free_id = 0

    for i in existing_ids:
        numeric_id = int(i[1:])  # Ignoriere das `#` am Anfang
        if numeric_id == min_free_id:
            min_free_id += 1  # Suche die nächste freie ID
        else:
            break
    formatted_character_id = f"#{min_free_id:04d}"
    return formatted_character_id

def validate_post_request(field_names, data):

    for topic in field_names:
        if topic not in data or not data[topic]:
            return topic
        else:
            for stat in data[topic]:
                for key, default_value in templates[field_names.index(topic)].items():
                    if key not in stat or stat[key] is None:
                        stat[key] = default_value
    return None


def generate_character_trait(name_list, trait_data, field):
    for trait in trait_data:
        if trait[f"{field}_name"] not in name_list:
            return Response({"error": f"Invalid trait name '{trait[f'{field}_name']}'."}, )
        else:
            name_list.remove(trait[f"{field}_name"])

    missing_traits = []
    for trait in name_list:
        if field == "attribute":
            trait_data.append(
                        {
                            f"{field}_name": trait,
                            f"{field}_value": 10,
                            f"{field}_adjustment": 0,
                        }
            )
        elif field == "saving_throw":
            trait_data.append(
                        {
                            f"{field}_name": trait,
                            f"{field}_adjustment": 0,
                            f"{field}_is_proficient": False,
                        }
            )
        elif field == "skill":
            trait_data.append(
                        {
                            f"{field}_name": trait,
                            f"{field}_adjustment": 0,
                            f"{field}_is_proficient": False,
                            f"{field}_is_expertise": False,
                        }
            )

    return missing_traits

def update_character_stats(data, data_db):

    for skill in skills_data:
        for skill_db in character_skills_db:
            if skill_db.skill_name == skill["skill_name"]:
                if "skill_adjustment" in skill:
                    skill_db.skill_adjustment = skill["skill_adjustment"]
                if "skill_is_proficient" in skill:
                    skill_db.skill_is_proficient = skill["skill_is_proficient"]
                if "skill_is_expertise" in skill:
                    skill_db.skill_is_expertise = skill["skill_is_expertise"]

