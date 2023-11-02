from django.core.paginator import Paginator
from django.shortcuts import render
from moonhr.models import *
from django.views.generic import ListView

PAGINATE_BY_CONST = 20


class ContactListView(ListView):
    paginate_by = PAGINATE_BY_CONST

    def __init__(self):
        self.currentUser = UserProfile.objects.get(is_selected=True)

    def get_candidates(self):
        astronauts = UserAstronaut.objects.filter(user__pk=self.currentUser.pk).filter(
            status=ASTRONAUT_STATUS_CHOISES.CANDIDATE)
        return astronauts

    def get_employees(self):
        astronauts = UserAstronaut.objects.filter(user__pk=self.currentUser.pk).exclude(
            status=ASTRONAUT_STATUS_CHOISES.CANDIDATE)
        return astronauts


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
    contacList = ContactListView()
    paginator = Paginator(contacList.get_candidates(),
                          contacList.paginate_by)

    to_hire_pk = request.GET.get("contact_pk_to_hire")
    if (to_hire_pk):
        userAstronaut = UserAstronaut.objects.get(pk=to_hire_pk)
        userAstronaut.status = ASTRONAUT_STATUS_CHOISES.READY
        userAstronaut.save()

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "moonhr/candidates.html", {"page_obj": page_obj})


def employees_view(request):
    contact_list = ContactListView()
    paginator = Paginator(contact_list.get_employees(),
                          contact_list.paginate_by)

    currentUser = UserProfile.objects.get(is_selected=True)
    missions = UserMission.objects.filter(
        user__pk=currentUser.pk).filter(status=MISSION_STATUS_CHOISES.NEW)

    user_astornaut_pk = request.GET.get("user_astornaut_pk")
    user_mission_pk = request.GET.get("user_mission_pk")

    if None not in (user_astornaut_pk, user_mission_pk):
        user_mission = missions.get(pk=user_mission_pk)
        user_mission.status = MISSION_STATUS_CHOISES.INPROGRESS
        user_astronaut = contact_list.get_employees().get(pk=user_astornaut_pk)
        user_astronaut.status = ASTRONAUT_STATUS_CHOISES.ONMISSION
        user_mission.astronaut = user_astronaut.astronaut
        astronaut_skills = AstronautSkill.objects.filter(
            astronaut__pk=user_mission.astronaut.pk)
        mission_results = MissionSkill.objects.filter(
            mission__pk=user_mission.mission.pk)
        results = set()
        for mission_result in mission_results:
            result = astronaut_skills.filter(
                skill=mission_result.skill).first()
            if (result):
                results.add(result)

        if (len(results) == 0):
            mission_result = mission_results.get(skills_used=0)
            user_mission.result = mission_result.result
        elif (len(results) == 1):
            mission_result = mission_results.filter(
                skills_used=1).get(skill=results.pop().skill)
            user_mission.result = mission_result.result
        else:
            mission_result = mission_results.filter(
                skills_used=2).get(skill=results.pop().skill)
            user_mission.result = mission_result.result

        user_mission.save()
        user_astronaut.save()

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "moonhr/employees.html", {"page_obj": page_obj, "missions_obj": missions})


def cv_view(request):
    to_view_pk = request.GET.get("contact_pk_to_view")
    currentUser = UserProfile.objects.get(is_selected=True)
    astronaut = UserAstronaut.objects.filter(
        user__pk=currentUser.pk).get(pk=to_view_pk)
    return render(request, "moonhr/cv.html", {"page_obj": astronaut})


def missions_view(request):
    mission_list = MissionListView()

    paginator = Paginator(mission_list.get_missions(),
                          mission_list.paginate_by)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "moonhr/missions.html", {"page_obj": page_obj})


DEFAULT_ASTRONAUT_NAME = "Constantine"
DEFAULT_ASTRONAUT_SURNAME = "Constantinopolus"


def mission_description_view(request):
    to_view_pk = request.GET.get("mission_pk_to_view")
    currentUser = UserProfile.objects.get(is_selected=True)
    mission = UserMission.objects.filter(
        user__pk=currentUser.pk).get(pk=to_view_pk)

    description = ""
    if (mission.result):
        description = mission.result.description
        astronaut_name = mission.astronaut.name
        astronaut_surname = mission.astronaut.surname
        description = description.replace(
            DEFAULT_ASTRONAUT_NAME, astronaut_name)
        description = description.replace(
            DEFAULT_ASTRONAUT_SURNAME, astronaut_surname)
        if (mission.astronaut.sex is str(SEX_CHOISES.FEMALE)):
            # he/him/his to she/her/hers
            description = description.replace(" he ", " she ").replace(" him ", " her ").replace(" his ", " her ")
            description = description.replace("He ", "She ").replace("Him ", "Her ").replace("Him ", "Her ")
            description = description.replace(" he.", " she.").replace(" him.", " her.").replace(" his.", " hers.")
   

    return render(request, "moonhr/mission-description.html", {"page_obj": mission, "description": description})
