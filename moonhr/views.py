from django.core.paginator import Paginator
from django.shortcuts import render
from moonhr.models import *
from django.views.generic import ListView

PAGINATE_BY_CONST = 20
TIME_DAY_END = 18


class AstronautWithTags:
    def __init__(self, user_astronaut):
        self.user_astronaut = user_astronaut
        self.tags = []


class ContactListView(ListView):
    paginate_by = PAGINATE_BY_CONST

    def __init__(self):
        self.current_user = UserProfile.objects.get(is_selected=True)

    def get_candidates(self):
        user_astronauts = UserAstronaut.objects.filter(user__pk=self.current_user.pk).filter(
            status=ASTRONAUT_STATUS_CHOISES.CANDIDATE
        )

        return self.add_tags(user_astronauts)

    def get_employees(self):
        user_astronauts = UserAstronaut.objects.filter(user__pk=self.current_user.pk).exclude(
            status=ASTRONAUT_STATUS_CHOISES.CANDIDATE
        )

        return self.add_tags(user_astronauts)

    def add_tags(self, user_astronauts):
        astronaut_with_tags = []
        for user_astronaut in user_astronauts:
            astronaut_with_tag = AstronautWithTags(user_astronaut)
            astronaut_with_tag.tags = UserAstronautTag.objects.filter(user_astronaut__pk=user_astronaut.pk)
            astronaut_with_tags.append(astronaut_with_tag)
        return astronaut_with_tags


class MissionListView(ListView):
    paginate_by = 1

    def __init__(self):
        self.current_user = UserProfile.objects.get(is_selected=True)

    def get_new_missions(self):
        missions = UserMission.objects.filter(user__pk=self.current_user.pk).filter(status=MISSION_STATUS_CHOISES.NEW)
        return missions

    def get_finished_missions(self):
        missions = UserMission.objects.filter(user__pk=self.current_user.pk).filter(
            status=MISSION_STATUS_CHOISES.FINISHED
        )
        return missions

    def get_inprogress_missions(self):
        missions = UserMission.objects.filter(user__pk=self.current_user.pk).filter(
            status=MISSION_STATUS_CHOISES.INPROGRESS
        )
        return missions


def home_view(request):
    current_user = UserProfile.objects.get(is_selected=True)

    reset_game = request.GET.get("reset_game")
    if reset_game == "1":
        mission_list = MissionListView()
        reset_missions(mission_list.get_finished_missions())
        reset_missions(mission_list.get_inprogress_missions())
        astranaut_list = ContactListView()
        astranaut_list.get_employees()
        for employee in astranaut_list.get_employees():
            employee.user_astronaut.status = ASTRONAUT_STATUS_CHOISES.CANDIDATE
            employee.user_astronaut.save()

        user_astronaut_tags = UserAstronautTag.objects.all()
        user_astronaut_tags.delete()

        current_user.score = 0
        current_user.time = 10
        current_user.day = 1
        current_user.week = 1
        current_user.save()

    finish_missions_get = request.GET.get("finish_missions")
    if finish_missions_get == "1":
        finish_missions()

    end_day = request.GET.get("end_day")
    if end_day == "1":
        current_user.time = 10
        current_user.day += 1
        current_user.save()

    end_week = request.GET.get("end_week")
    if end_week == "1":
        current_user.time = 10
        current_user.day = 1
        current_user.week += 1
        current_user.save()

        finish_missions()

    current_user = UserProfile.objects.get(is_selected=True)
    time = {"time": current_user.time, "day": current_user.day, "week": current_user.week}
    return render(request, "moonhr/home.html", {"score": current_user.score, "time": time})

def finish_missions():
    current_user = UserProfile.objects.get(is_selected=True)
    mission_list = MissionListView()
    missions = mission_list.get_inprogress_missions()
    for mission in missions:
        mission.status = MISSION_STATUS_CHOISES.FINISHED
        current_user.score += mission.result.score
        current_user.save()
        mission.save()

    user_astronauts = UserAstronaut.objects.filter(user__pk=current_user.pk).filter(
            status=ASTRONAUT_STATUS_CHOISES.ONMISSION
        )
    for user_astronaut in user_astronauts:
        user_astronaut.status = ASTRONAUT_STATUS_CHOISES.READY
        user_astronaut.save()


def reset_missions(missions):
    for mission in missions:
        mission.result = None
        mission.astronaut = None
        mission.status = MISSION_STATUS_CHOISES.NEW
        mission.save()


def candidates_view(request):
    current_user = UserProfile.objects.get(is_selected=True)

    if current_user.time < 18:
        hire_astronaut(request)

    current_user = UserProfile.objects.get(is_selected=True)
    message = f"Current time: {current_user.time}:00."
    if current_user.time < 18:
        message += " You can hire astronauts."
    else:
        message += " Day time is over. You can't hire more today."

    contac_list = ContactListView()
    paginator = Paginator(contac_list.get_candidates(), contac_list.paginate_by)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "moonhr/candidates.html", {"page_obj": page_obj, "message": message})


def hire_astronaut(request):
    to_hire_pk = request.GET.get("contact_pk_to_hire")
    if to_hire_pk:
        userAstronaut = UserAstronaut.objects.get(pk=to_hire_pk)
        userAstronaut.status = ASTRONAUT_STATUS_CHOISES.READY
        userAstronaut.save()
        current_user = UserProfile.objects.get(is_selected=True)
        current_user.time += 2
        current_user.save()


def employees_view(request):
    contact_list = ContactListView()
    paginator = Paginator(contact_list.get_employees(), contact_list.paginate_by)

    current_user = UserProfile.objects.get(is_selected=True)
    user_missions = UserMission.objects.filter(user__pk=current_user.pk).filter(status=MISSION_STATUS_CHOISES.NEW)

    send_to_mission(request, user_missions)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "moonhr/employees.html", {"page_obj": page_obj, "user_missions": user_missions})


def send_to_mission(request, user_missions):
    user_astornaut_pk = request.GET.get("user_astornaut_pk")
    user_mission_pk = request.GET.get("user_mission_pk")

    if None not in (user_astornaut_pk, user_mission_pk):
        user_mission = user_missions.get(pk=user_mission_pk)
        user_mission.status = MISSION_STATUS_CHOISES.INPROGRESS
        user_astronaut = UserAstronaut.objects.get(pk=user_astornaut_pk)
        user_astronaut.status = ASTRONAUT_STATUS_CHOISES.ONMISSION
        user_mission.astronaut = user_astronaut.astronaut
        astronaut_skills = AstronautSkill.objects.filter(astronaut__pk=user_mission.astronaut.pk)
        mission_skill_results = MissionSkillResult.objects.filter(mission__pk=user_mission.mission.pk)
        results = set()
        for mission_skill_result in mission_skill_results:
            result = astronaut_skills.filter(skill=mission_skill_result.skill).first()
            if result:
                results.add(result)

        if len(results) == 0:
            mission_skill_result = mission_skill_results.get(skills_used=0)
            user_mission.result = mission_skill_result.result
        elif len(results) == 1:
            mission_skill_result = mission_skill_results.filter(skills_used=1).get(skill=results.pop().skill)
            user_mission.result = mission_skill_result.result

        else:
            mission_skill_result = mission_skill_results.filter(skills_used=2).get(skill=results.pop().skill)
            user_mission.result = mission_skill_result.result

        current_user = UserProfile.objects.get(is_selected=True)
        current_user.time += 2
        current_user.save()

        user_mission.save()
        user_astronaut.save()


def cv_view(request):
    to_view_pk = request.GET.get("contact_pk_to_view")
    user_astronaut = UserAstronaut.objects.get(pk=to_view_pk)

    add_tag(request, user_astronaut)

    more_tags = Skill.objects.all()
    user_astronaut_tags = UserAstronautTag.objects.filter(user_astronaut__pk=user_astronaut.pk)
    tags_menu_obj = {"user_astronaut_tags": user_astronaut_tags, "more_tags": more_tags, "get_page": "/cv/"}

    return render(
        request,
        "moonhr/cv.html",
        {"user_astronaut": user_astronaut, "tags_menu_obj": tags_menu_obj},
    )


def add_tag(request, user_astronaut):
    tag_to_add_pk = request.GET.get("skill_tag_pk")
    if tag_to_add_pk:
        skill_tag_to_add = Skill.objects.get(pk=tag_to_add_pk)
        user_astronaut_tag = UserAstronautTag()
        user_astronaut_tag.user_astronaut = user_astronaut
        user_astronaut_tag.tag = skill_tag_to_add
        user_astronaut_tag.save()


def missions_view(request):
    contact_list = ContactListView()
    current_user = UserProfile.objects.get(is_selected=True)
    user_missions = UserMission.objects.filter(user__pk=current_user.pk).filter(status=MISSION_STATUS_CHOISES.NEW)

    if current_user.time < 18:
        send_to_mission(request, user_missions)

    mission_list = MissionListView()
    paginator = Paginator(mission_list.get_new_missions(), mission_list.paginate_by)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    user_astronauts = contact_list.get_employees()

    current_user = UserProfile.objects.get(is_selected=True)
    message = f"Current time: {current_user.time}:00."
    if current_user.time < 18:
        message += " You can send astronauts to missions."
    else:
        message += " Day time is over. You can't start more missions today."

    return render(
        request,
        "moonhr/missions.html",
        {
            "page_obj": page_obj,
            "user_astronauts": user_astronauts,
            "user_missions": user_missions,
            "astronauts_count": len(user_astronauts) if user_astronauts else 0,
            "message": message,
        },
    )


class MissionWithDescription:
    def __init__(self, user_mission, description):
        self.user_mission = user_mission
        self.description = description


def finished_missions_view(request):
    mission_list = MissionListView()
    finished_missions = mission_list.get_finished_missions()
    finished_missions_with_descrition = []
    for finished_mission in finished_missions:
        description = correct_description(finished_mission)
        finished_missions_with_descrition.append(MissionWithDescription(finished_mission, description))

    paginator = Paginator(finished_missions_with_descrition, mission_list.paginate_by)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "moonhr/finished-missions.html", {"page_obj": page_obj})


DEFAULT_ASTRONAUT_NAME = "Constantine"
DEFAULT_ASTRONAUT_SURNAME = "Constantinopolus"


def mission_description_view(request):
    to_view_pk = request.GET.get("mission_pk_to_view")
    current_user = UserProfile.objects.get(is_selected=True)
    mission = UserMission.objects.filter(user__pk=current_user.pk).get(pk=to_view_pk)

    description = correct_description(mission)

    return render(request, "moonhr/mission-description.html", {"page_obj": mission, "description": description})


def correct_description(mission):
    description = ""
    if mission.result:
        description = mission.result.description
        astronaut_name = mission.astronaut.name
        astronaut_surname = mission.astronaut.surname
        description = description.replace(DEFAULT_ASTRONAUT_NAME, astronaut_name)
        description = description.replace(DEFAULT_ASTRONAUT_SURNAME, astronaut_surname)
        if mission.astronaut.sex is str(SEX_CHOISES.FEMALE):
            # he/him/his to she/her/hers
            description = description.replace(" he ", " she ").replace(" him ", " her ").replace(" his ", " her ")
            description = description.replace("He ", "She ").replace("Him ", "Her ").replace("Him ", "Her ")
            description = description.replace(" he.", " she.").replace(" him.", " her.").replace(" his.", " hers.")
    return description
