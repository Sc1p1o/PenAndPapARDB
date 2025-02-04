from django.db import models

class Attributes(models.Model):
    attribute_name = models.CharField(max_length=20)
    attribute_value = models.PositiveSmallIntegerField(default=10)
    attribute_adjustment = models.PositiveSmallIntegerField(default=0)

class SavingThrowProficiencies(models.Model):
    saving_throw_name = models.CharField(max_length=20)
    saving_throw_adjustment = models.PositiveSmallIntegerField(default=0)
    saving_throw_is_proficient = models.BooleanField(default=False)

class Skills(models.Model):
    skill_name = models.CharField(max_length=20)
    skill_adjustment = models.PositiveSmallIntegerField(default=0)
    skill_is_proficient = models.BooleanField(default=False)
    skill_is_expertise = models.BooleanField(default=False)

class CharacterStats(models.Model):
    character_armor_class = models.PositiveSmallIntegerField(default=10)
    character_hit_points = models.PositiveSmallIntegerField(default=10)
    character_movement_speed = models.PositiveSmallIntegerField(default=30)
    character_is_inspired = models.BooleanField(default=False)
    character_name = models.CharField(max_length=50)
    character_class = models.CharField(max_length=50)
    character_race = models.CharField(max_length=50)
    character_background = models.CharField(max_length=50)
    character_subclass = models.CharField(max_length=50)
    character_level = models.PositiveSmallIntegerField(default=3)

    character_conditions = models.CharField(max_length=50)
