from django.db import models


class SkillDescription(models.Model):
    skillName = models.CharField(max_length=64, unique=True)
    skillDesc = models.TextField(default="")

    def __str__(self):
        return f"{self.skillName}"


class MissionRequestParameters(models.Model):
    place = models.CharField(max_length=64)
    who = models.CharField(max_length=64)
    task = models.CharField(max_length=256)
    description = models.TextField(default="")
    skillOne = models.ForeignKey(
        SkillDescription, related_name='%(class)s_skill_one', on_delete=models.PROTECT)
    skillTwo = models.ForeignKey(
        SkillDescription, related_name='%(class)s_skill_two', on_delete=models.PROTECT)

    def __str__(self):
        return f"In {self.place} do {self.task} "


class Astronaut(models.Model):
    name = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)
    sex = models.CharField(max_length=16)
    cv = models.TextField(default="")
    skillOne = models.ForeignKey(
        SkillDescription, related_name='%(class)s_skill_one', on_delete=models.PROTECT, null=True)
    skillTwo = models.ForeignKey(
        SkillDescription, related_name='%(class)s_skill_two', on_delete=models.PROTECT, null=True)
    skillThree = models.ForeignKey(
        SkillDescription, related_name='%(class)s_skill_three', on_delete=models.PROTECT, null=True)
    skillFour = models.ForeignKey(
        SkillDescription, related_name='%(class)s_skill_four', on_delete=models.PROTECT, null=True)
    status = models.CharField(max_length=32) 

    def __str__(self):
        return f"{self.name} {self.surname}"


class MissionDebriefing(models.Model):
    parameters = models.ForeignKey(
        MissionRequestParameters, on_delete=models.PROTECT)
    results00 = models.TextField(default="")
    results10 = models.TextField(default="")
    results01 = models.TextField(default="")
    results11 = models.TextField(default="")

    def __str__(self):
        return f"In {self.parameters.place} {self.parameters.task} done"
