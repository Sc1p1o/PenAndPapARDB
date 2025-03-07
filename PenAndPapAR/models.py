from django.db import models

class CharacterStats(models.Model):
    character_id = models.AutoField(primary_key=True)
    character_is_inspired = models.BooleanField(default=False, null=True)
    character_name = models.CharField(max_length=50, null=True)
    character_class = models.CharField(max_length=50, null=True)
    character_race = models.CharField(max_length=50, null=True)
    character_background = models.CharField(max_length=50, null=True)
    character_subclass = models.CharField(max_length=50, null=True)
    character_level = models.PositiveSmallIntegerField(default=3, null=True)
    character_alignment = models.CharField(max_length=50, null=True)
    character_conditions = models.TextField(null=True)

class Attributes(models.Model):
    attribute_name = models.CharField(max_length=20)
    attribute_value = models.PositiveSmallIntegerField(default=10)
    attribute_adjustment = models.PositiveSmallIntegerField(default=0)
    attribute_charakter = models.ForeignKey(CharacterStats, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('attribute_name', 'attribute_charakter')


class AC(models.Model):
    AC_base = models.CharField(max_length=20)
    AC_modified = models.PositiveSmallIntegerField(default=10)
    ac_charakter = models.OneToOneField(CharacterStats, on_delete=models.CASCADE, related_name="ac")


class SavingThrowProficiencies(models.Model):
    saving_throw_name = models.CharField(max_length=20, primary_key=True)
    saving_throw_adjustment = models.PositiveSmallIntegerField(default=0)
    saving_throw_is_proficient = models.BooleanField(default=False)
    saving_throw_proficiency_charakter = models.ForeignKey(CharacterStats, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('saving_throw_name', 'saving_throw_proficiency_charakter')

class Skills(models.Model):
    skill_name = models.CharField(max_length=20, primary_key=True)
    skill_adjustment = models.PositiveSmallIntegerField(default=0)
    skill_is_proficient = models.BooleanField(default=False)
    skill_is_expertise = models.BooleanField(default=False)
    skills_charakter = models.ForeignKey(CharacterStats, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('skill_name', 'skills_charakter')

class HitPoints(models.Model):
    hit_points_current = models.PositiveSmallIntegerField(default=10)
    hit_points_max = models.PositiveSmallIntegerField(default=10)
    hit_points_temp = models.PositiveSmallIntegerField(default=0)
    non_lethal_damage = models.PositiveSmallIntegerField(default=0)
    hit_points_charakter = models.OneToOneField(CharacterStats, on_delete=models.CASCADE, related_name="hit_points")

