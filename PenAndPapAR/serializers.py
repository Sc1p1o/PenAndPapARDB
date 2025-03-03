# PenAndPapAR/serializers.py
from rest_framework import serializers

from PenAndPapAR.models import CharacterStats


class CharacterStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterStats
        fields = '__all__'