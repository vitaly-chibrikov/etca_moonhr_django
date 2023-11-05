from django.core.paginator import Paginator
from django.shortcuts import render
from moonhr.models import *
from django.views.generic import ListView

PAGINATE_BY_CONST = 20

class AstronautWithTags:
    def __init__(self, user_astronaut):
        self.user_astronaut = user_astronaut
        self.tags = []


class ContactListView(ListView):
    paginate_by = PAGINATE_BY_CONST

    def __init__(self):
        self.currentUser = UserProfile.objects.get(is_selected=True)

    def get_candidates(self):
        user_astronauts = UserAstronaut.objects.filter(user__pk=self.currentUser.pk).filter(
            status=ASTRONAUT_STATUS_CHOISES.CANDIDATE
        )

        return self.add_tags(user_astronauts)

    

    def get_employees(self):
        user_astronauts = UserAstronaut.objects.filter(user__pk=self.currentUser.pk).exclude(
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
    paginate_by = PAGINATE_BY_CONST

    def __init__(self):
        self.currentUser = UserProfile.objects.get(is_selected=True)

    def get_missions(self):
        missions = UserMission.objects.filter(user__pk=self.currentUser.pk)
        return missions


def home_view(request):
    return render(request, "moonhr/home.html")


def candidates_view(request):
    hire_astronaut(request)

    contac_list = ContactListView()
    paginator = Paginator(contac_list.get_candidates(), contac_list.paginate_by)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "moonhr/candidates.html", {"page_obj": page_obj})


def hire_astronaut(request):
    to_hire_pk = request.GET.get("contact_pk_to_hire")
    if to_hire_pk:
        userAstronaut = UserAstronaut.objects.get(pk=to_hire_pk)
        userAstronaut.status = ASTRONAUT_STATUS_CHOISES.READY
        userAstronaut.save()


def employees_view(request):
    contact_list = ContactListView()
    paginator = Paginator(contact_list.get_employees(), contact_list.paginate_by)

    current_user = UserProfile.objects.get(is_selected=True)
    user_missions = UserMission.objects.filter(user__pk=current_user.pk).filter(status=MISSION_STATUS_CHOISES.NEW)

    send_to_mission(request, contact_list, user_missions)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "moonhr/employees.html", {"page_obj": page_obj, "missions_obj": user_missions})


def send_to_mission(request, contact_list, user_missions):
    user_astornaut_pk = request.GET.get("user_astornaut_pk")
    user_mission_pk = request.GET.get("user_mission_pk")

    if None not in (user_astornaut_pk, user_mission_pk):
        user_mission = user_missions.get(pk=user_mission_pk)
        user_mission.status = MISSION_STATUS_CHOISES.INPROGRESS
        user_astronaut = contact_list.get_employees().get(pk=user_astornaut_pk)
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
    mission_list = MissionListView()

    paginator = Paginator(mission_list.get_missions(), mission_list.paginate_by)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "moonhr/missions.html", {"page_obj": page_obj})


DEFAULT_ASTRONAUT_NAME = "Constantine"
DEFAULT_ASTRONAUT_SURNAME = "Constantinopolus"


def mission_description_view(request):
    to_view_pk = request.GET.get("mission_pk_to_view")
    current_user = UserProfile.objects.get(is_selected=True)
    mission = UserMission.objects.filter(user__pk=current_user.pk).get(pk=to_view_pk)

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

    return render(request, "moonhr/mission-description.html", {"page_obj": mission, "description": description})
