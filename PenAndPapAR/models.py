from django.db import models

class CharacterStats(models.Model):
    character_id = models.AutoField(primary_key=True)
    character_is_inspired = models.BooleanField(default=False)
    character_name = models.CharField(max_length=50)
    character_class = models.CharField(max_length=50)
    character_race = models.CharField(max_length=50)
    character_background = models.CharField(max_length=50)
    character_subclass = models.CharField(max_length=50)
    character_level = models.PositiveSmallIntegerField(default=3)
    character_alignment = models.CharField(max_length=50)
    character_conditions = models.TextField()

class Attributes(models.Model):
    attribute_name = models.CharField(max_length=20, primary_key=True)
    attribute_value = models.PositiveSmallIntegerField(default=10)
    attribute_adjustment = models.PositiveSmallIntegerField(default=0)
    attribute_charakter = models.ForeignKey(CharacterStats, on_delete=models.CASCADE)

class AC(models.Model):
    AC_base = models.CharField(max_length=20, primary_key=True)
    AC_modified = models.PositiveSmallIntegerField(default=10)
    attribute_charakter = models.ForeignKey(CharacterStats, on_delete=models.CASCADE)

class SavingThrowProficiencies(models.Model):
    saving_throw_name = models.CharField(max_length=20, primary_key=True)
    saving_throw_adjustment = models.PositiveSmallIntegerField(default=0)
    saving_throw_is_proficient = models.BooleanField(default=False)
    attribute_charakter = models.ForeignKey(CharacterStats, on_delete=models.CASCADE)

class Skills(models.Model):
    skill_name = models.CharField(max_length=20, primary_key=True)
    skill_adjustment = models.PositiveSmallIntegerField(default=0)
    skill_is_proficient = models.BooleanField(default=False)
    skill_is_expertise = models.BooleanField(default=False)
    attribute_charakter = models.ForeignKey(CharacterStats, on_delete=models.CASCADE)

class HitPoints(models.Model):
    hit_points_current = models.PositiveSmallIntegerField(default=10)
    hit_points_max = models.PositiveSmallIntegerField(default=10)
    hit_points_temp = models.PositiveSmallIntegerField(default=0)
    non_lethal_damage = models.PositiveSmallIntegerField(default=0)
    attribute_charakter = models.ForeignKey(CharacterStats, on_delete=models.CASCADE)


"""
class Items(models.Model):
    # Item Characteristics
    item_name = models.CharField(max_length=50, primary_key=True)
    item_weight = models.PositiveSmallIntegerField(default=10)
    item_value = models.PositiveSmallIntegerField(default=10)
    item_is_equipped = models.BooleanField(default=False)

    # Modifiers
    item_modified_skills = models.ManyToManyField('Skills', related_name='item_modified_skills')
    item_modified_attributes = models.ManyToManyField('Attributes', related_name='item_modified_attributes')
    item_modified_saving_throws = models.ManyToManyField('SavingThrowProficiencies',
                                                         related_name='item_modified_saving_throws')
    item_modified_stats = models.ManyToManyField('CharacterStats', related_name='item_modified_stats')

class Feats(models.Model):
    # Item Characteristics
    feat_name = models.CharField(max_length=50, primary_key=True)
    feat_description = models.TextField()

    # Modifiers
    feat_modified_skills = models.ManyToManyField('Skills', related_name='feat_modified_skills')
    feat_modified_attributes = models.ManyToManyField('Attributes', related_name='feat_modified_attributes')
    feat_modified_saving_throws = models.ManyToManyField('SavingThrowProficiencies',
                                                         related_name='feat_modified_saving_throws')
    feat_modified_stats = models.ManyToManyField('CharacterStats', related_name='feat_modified_stats')
"""