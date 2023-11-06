from django.db import models


class SEX_CHOISES(models.TextChoices):
    MALE = ("Male", "Male")
    FEMALE = ("Female", "Female")


class ASTRONAUT_STATUS_CHOISES(models.TextChoices):
    CANDIDATE = ("Candidate", "Candidate")
    READY = ("Ready", "Ready")
    ONMISSION = ("On mission", "On mission")


class MISSION_STATUS_CHOISES(models.TextChoices):
    NEW = ("New", "New")
    INPROGRESS = ("In progress", "In progress")
    FINISHED = ("Finished", "Finished")


class Skill(models.Model):
    name = models.CharField(max_length=64, unique=True)
    desc = models.TextField(default="")
    tag = models.CharField(max_length=16, default="")

    def __str__(self):
        return f"{self.name}"


class Place(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(default="")

    def __str__(self):
        return f"{self.name}"


class Mission(models.Model):
    place = models.ForeignKey(Place, on_delete=models.PROTECT)
    who = models.CharField(max_length=64)
    task = models.CharField(max_length=256)
    description = models.TextField(default="")

    def __str__(self):
        return f"In {self.place} do {self.task} "


class Astronaut(models.Model):
    name = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)
    sex = models.CharField(max_length=16, choices=SEX_CHOISES.choices, default=SEX_CHOISES.MALE)
    cv = models.TextField(default="")

    def __str__(self):
        return f"{self.name} {self.surname}"


class UserProfile(models.Model):
    user_name = models.CharField(max_length=64)
    hours_passed = models.SmallIntegerField()
    is_selected = models.BooleanField(default=False)
    score = models.SmallIntegerField(default=0) 

    def __str__(self):
        return f"{self.user_name}"


class UserAstronaut(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.PROTECT)
    astronaut = models.ForeignKey(Astronaut, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=16, choices=ASTRONAUT_STATUS_CHOISES.choices, default=ASTRONAUT_STATUS_CHOISES.CANDIDATE
    )

    def __str__(self):
        return f"{self.user.user_name} -> {self.astronaut.name} {self.astronaut.surname} -> {self.status}"


class UserAstronautTag(models.Model):
    user_astronaut = models.ForeignKey(UserAstronaut, on_delete=models.PROTECT)
    tag = models.ForeignKey(Skill, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.user_astronaut.user.user_name} -> {self.user_astronaut.astronaut.name} {self.user_astronaut.astronaut.surname} -> {self.tag.tag}"


class AstronautSkill(models.Model):
    astronaut = models.ForeignKey(Astronaut, on_delete=models.PROTECT)
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.astronaut.name} {self.astronaut.surname} -> {self.skill.name}"


class MissionResult(models.Model):
    description = models.TextField(default="")
    comments = models.TextField(default="")
    score = models.SmallIntegerField(default = 1) 

    def __str__(self):
        return f"{self.comments} {self.score}"


class MissionSkillResult(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.PROTECT)
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT, null=True, default=None, blank=True)
    result = models.ForeignKey(MissionResult, on_delete=models.PROTECT, null=True, default=None, blank=True)
    skills_used = models.SmallIntegerField(default=0)

    def __str__(self):
        return f"{self.mission.place} {self.mission.task} -> {self.result.comments if self.result else ''} -> ({self.skills_used}) -> SKILL: {self.skill.name if self.skill else 'None'} "


class UserMission(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.PROTECT)
    mission = models.ForeignKey(Mission, on_delete=models.PROTECT)
    status = models.CharField(max_length=16, choices=MISSION_STATUS_CHOISES.choices, default=MISSION_STATUS_CHOISES.NEW)
    astronaut = models.ForeignKey(Astronaut, on_delete=models.PROTECT, null=True, blank=True)
    result = models.ForeignKey(MissionResult, on_delete=models.PROTECT, null=True, default=None, blank=True)

    def __str__(self):
        return f"{self.user.user_name} -> {self.mission} -> {self.status}"
