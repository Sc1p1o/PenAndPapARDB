from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from PenAndPapAR.models import Attributes
from PenAndPapAR.serializers import CharacterStatsSerializer


class CharacterStatsView(APIView):
    def get(self, request):
        character_stats = CharacterStatsSerializer.objects.all()
        serializer = CharacterStatsSerializer(character_stats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CharacterStatsSerializer(data=request.data)
        if serializer.is_valid():
            character = serializer.save()

            attributes = request.data.get('attributes', [])
            if attributes:
                for attr in attributes:
                    Attributes.objects.create(
                        attribute_name=attr.get("attribute_name"),
                        attribute_value=attr.get("attribute_value", 10),  # Standardwert, falls nicht angegeben
                        attribute_charakter=character,
                    )
            else:
                # Standardattribute erstellen, falls keine angegeben wurden
                default_attributes = [
                    {"attribute_name": "Strength", "attribute_value": 10},
                    {"attribute_name": "Dexterity", "attribute_value": 10},
                    {"attribute_name": "Constitution", "attribute_value": 10},
                    {"attribute_name": "Intelligence", "attribute_value": 10},
                    {"attribute_name": "Wisdom", "attribute_value": 10},
                    {"attribute_name": "Charisma", "attribute_value": 10},
                ]

                for attr in default_attributes:
                    Attributes.objects.create(
                        attribute_name=attr["attribute_name"],
                        attribute_value=attr["attribute_value"],
                        attribute_charakter=character,
                    )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


