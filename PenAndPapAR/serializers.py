# PenAndPapAR/serializers.py
from rest_framework import serializers

from PenAndPapAR.models import CharacterStats, Attributes, AC, SavingThrowProficiencies, Skills, HitPoints

class CharacterStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterStats
        fields = '__all__'

class AttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attributes
        fields = '__all__'

class ACSerializer(serializers.ModelSerializer):
    class Meta:
        model = AC
        fields = '__all__'

class SavingThrowProficienciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingThrowProficiencies
        fields = '__all__'

class SkillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skills
        fields = '__all__'

class HitPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HitPoints
        fields = '__all__'