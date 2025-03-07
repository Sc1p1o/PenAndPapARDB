from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

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
    "character_class": "Unknown",
    "character_race": "Unknown",
    "character_background": "Unknown",
    "character_subclass": "None",
    "character_level": 1,
    "character_alignment": "Neutral",
    "character_conditions": "Healthy"
}

attribute_template = {
    "attribute_name": "Strength",
    "attribute_value": 10,
    "attribute_adjustment": 0
}

ac_template = {
    "AC_base": "Base",
    "AC_modified": 10
}

saving_throw_proficiencies_template = {
    "saving_throw_name": "Strength",
    "saving_throw_adjustment": 0,
    "saving_throw_is_proficient": False}

skills_template = {
    "skill_name": "Athletics",
    "skill_adjustment": 0,
    "skill_is_proficient": False,
    "skill_is_expertise": False
}

hit_points_template = {
    "hit_points_current": 10,
    "hit_points_max": 10,
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
    def get(self, request):
        character_stats = CharacterStats.objects.all()
        character_attributes = Attributes.objects.all()
        character_ac = AC.objects.all()
        character_saving_throw_proficiencies = SavingThrowProficiencies.objects.all()
        character_skills = Skills.objects.all()
        character_hit_points = HitPoints.objects.all()

        stats_serializer = CharacterStatsSerializer(character_stats, many=True)
        attributes_serializer = AttributesSerializer(character_attributes, many=True)
        ac_serializer = ACSerializer(character_ac, many=True)
        saving_throw_proficiencies_serializer = SavingThrowProficienciesSerializer(character_saving_throw_proficiencies,
                                                                                   many=True)
        skills_serializer = SkillsSerializer(character_skills, many=True)
        hit_points_serializer = HitPointsSerializer(character_hit_points, many=True)


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
        # Lade die übergebenen Daten in den Serializer, um nur die CharacterStats zu erstellen
        data = request.data

        topics = ["stats", "attributes", "ac", "saving_throw_proficiencies", "skills", "hit_points",]

        for topic in topics:
            if topic not in data or not data[topic]:
                data[topic] = [templates[topics.index(topic)]]

            for stat in data[topic]:
                for key, default_value in templates[topics.index(topic)].items():
                    if key not in stat or stat[key] is None:
                        stat[key] = default_value

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

        if stats_serializer.is_valid():
            stats_serializer.save()
        else:
            return Response({"error": "Invalid data in stats."}, status=status.HTTP_400_BAD_REQUEST)

        if attributes_serializer.is_valid():
            attributes_serializer.save()
        else:
            return Response({"error": "Invalid data in attribute."}, status=status.HTTP_400_BAD_REQUEST)

        if ac_serializer.is_valid():
            ac_serializer.save()
        else:
            return Response({"error": "Invalid data in ac."}, status=status.HTTP_400_BAD_REQUEST)

        if saving_throw_proficiencies_serializer.is_valid():
            saving_throw_proficiencies_serializer.save()
        else:
            return Response({"error": "Invalid data in saving throws."}, status=status.HTTP_400_BAD_REQUEST)

        if skills_serializer.is_valid():
            skills_serializer.save()
        else:
            return Response({"error": "Invalid data in skills."}, status=status.HTTP_400_BAD_REQUEST)

        if hit_points_serializer.is_valid():
            hit_points_serializer.save()
        else:
            return Response({"error": "Invalid data in hit points."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Data has been successfully processed."}, status=status.HTTP_200_OK)


    def put(self, request, character_id):
        try:
            # Bestehenden Charakter abrufen
            character = CharacterStatsSerializer.objects.get(pk=character_id)

            # Charakterdaten aktualisieren, falls im Request-Body enthalten
            serializer = CharacterStatsSerializer(character, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

            # Attribute aktualisieren, falls sie im Request enthalten sind
            attributes = request.data.get('attributes', [])
            for attr in attributes:
                # Attribut für den Charakter abrufen
                try:
                    attribute = Attributes.objects.get(attribute_name=attr["attribute_name"],
                                                       attribute_charakter=character)

                    # Attribut-Wert aktualisieren
                    attribute.attribute_value = attr.get("attribute_value", attribute.attribute_value)
                    attribute.save()

                except Attributes.DoesNotExist:
                    raise Exception("Attribute not found.")

            return Response({"message": "Character and attributes updated successfully."}, status=status.HTTP_200_OK)

        except CharacterStatsSerializer.DoesNotExist:
            return Response({"error": "Character not found."}, status=status.HTTP_404_NOT_FOUND)


def checkDataInRequest(character_topic, counter):
    for topic in character_topic:
        print(f"{topic}\n")


def validateTopic(template, content):
    for stat in template:
        if stat not in content:
            print("")
