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
    TIME_DAY_END = 18
    TIME_DAY_START = 10
    DEFAULT_DAY = 1
    DEFAULT_WEEK = 1
    DEFAULT_SCORE = 0
    HOURS_PER_ACTION = 2

    user_name = models.CharField(max_length=64)
    is_selected = models.BooleanField(default=False)
    time = models.SmallIntegerField(default=TIME_DAY_START)
    day = models.SmallIntegerField(default=DEFAULT_DAY)
    week = models.SmallIntegerField(default=DEFAULT_WEEK)
    score = models.SmallIntegerField(default=DEFAULT_SCORE)

    def get_current():
        return UserProfile.objects.get(is_selected=True)
    
    def addEvent(self, description):
        event = UserEvent()
        event.user = self
        event.time = self.time
        event.day = self.day
        event.week = self.week
        event.description = description 
        event.save()

    def reset(self):
        self.score = UserProfile.DEFAULT_SCORE
        self.time = UserProfile.TIME_DAY_START
        self.day = UserProfile.DEFAULT_DAY
        self.week = UserProfile.DEFAULT_WEEK
        self.save()

    def do_work(self):
        self.time += UserProfile.HOURS_PER_ACTION
        self.save()

    def end_day(self):
        self.time = UserProfile.TIME_DAY_START
        self.day += 1
        self.save()

    def end_week(self):
        self.time = UserProfile.TIME_DAY_START
        self.day = 1
        self.week += 1
        self.save()

    def __str__(self):
        return f"{self.user_name}"

class UserEvent(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.PROTECT)
    time = models.SmallIntegerField(default=UserProfile.TIME_DAY_START)
    day = models.SmallIntegerField(default=UserProfile.DEFAULT_DAY)
    week = models.SmallIntegerField(default=UserProfile.DEFAULT_WEEK)
    description = models.TextField(default="")

    def __str__(self):
        return f"{self.user.user_name} week: {self.week} day: {self.day} time: {self.time}"

class UserAstronaut(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.PROTECT)
    astronaut = models.ForeignKey(Astronaut, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=16, choices=ASTRONAUT_STATUS_CHOISES.choices, default=ASTRONAUT_STATUS_CHOISES.CANDIDATE
    )

    def change_status(self, status, description):
        self.status = status
        self.user.addEvent(description)

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
    score = models.SmallIntegerField(default=1)

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
    DEFAULT_WEEKS_TO_END = 2
    DEFAULT_ASTRONAUT_NAME = "Constantine"
    DEFAULT_ASTRONAUT_SURNAME = "Constantinopolus"

    user = models.ForeignKey(UserProfile, on_delete=models.PROTECT)
    mission = models.ForeignKey(Mission, on_delete=models.PROTECT)
    status = models.CharField(max_length=16, choices=MISSION_STATUS_CHOISES.choices, default=MISSION_STATUS_CHOISES.NEW)
    astronaut = models.ForeignKey(Astronaut, on_delete=models.PROTECT, null=True, blank=True)
    result = models.ForeignKey(MissionResult, on_delete=models.PROTECT, null=True, default=None, blank=True)
    weeks_to_end = models.SmallIntegerField(default=DEFAULT_WEEKS_TO_END)

    def change_status(self, status, description):
        self.status = status
        self.user.addEvent(description)

    def correct_description(self):
        description = ""
        if self.result:
            description = self.result.description
            astronaut_name = self.astronaut.name
            astronaut_surname = self.astronaut.surname
            description = description.replace(UserMission.DEFAULT_ASTRONAUT_NAME, astronaut_name)
            description = description.replace(UserMission.DEFAULT_ASTRONAUT_SURNAME, astronaut_surname)
            if self.astronaut.sex is str(SEX_CHOISES.FEMALE):
                # he/him/his to she/her/hers
                description = description.replace(" he ", " she ").replace(" him ", " her ").replace(" his ", " her ")
                description = description.replace("He ", "She ").replace("Him ", "Her ").replace("Him ", "Her ")
                description = description.replace(" he.", " she.").replace(" him.", " her.").replace(" his.", " hers.")
        return description

    def __str__(self):
        return f"{self.user.user_name} -> {self.mission} -> {self.status}"
