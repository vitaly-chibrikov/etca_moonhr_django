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
        self.current_user = UserProfile.get_current()

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

    def get_ready(self):
        user_astronauts = UserAstronaut.objects.filter(user__pk=self.current_user.pk).filter(
            status=ASTRONAUT_STATUS_CHOISES.READY
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
        self.current_user = UserProfile.get_current()

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
    current_user = UserProfile.get_current()

    new_user_name = request.POST.get("new_user")
    if new_user_name:
        new_user = UserProfile()
        new_user.user_name = new_user_name
        new_user.is_selected = True
        current_user.is_selected = False
        current_user.save()
        new_user.save()
        current_user = UserProfile.get_current()
    
    reset_game = request.POST.get("reset_game")
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

        user_events = UserEvent.objects.all()
        user_events.delete()

        current_user.reset()

    finish_missions_get = request.POST.get("finish_missions")
    if finish_missions_get == "1":
        finish_missions()

    end_day = request.POST.get("end_day")
    if end_day == "1":
        current_user.end_day()

    end_week = request.POST.get("end_week")
    if end_week == "1":
        current_user.end_week()
        mission_list = MissionListView()
        user_missions = mission_list.get_inprogress_missions()
        for user_mission in user_missions:
            user_mission.weeks_to_end -= 1
            if user_mission.weeks_to_end == 0:
                user_mission.change_status(
                    MISSION_STATUS_CHOISES.FINISHED,
                    f"{user_mission.astronaut} finished mission in {user_mission.mission.place}",
                )
                current_user.score += user_mission.result.score
                user_astronaut = UserAstronaut.objects.filter(user__pk=current_user.pk).get(
                    astronaut__pk=user_mission.astronaut.pk
                )
                user_astronaut.change_status(
                    ASTRONAUT_STATUS_CHOISES.READY, f"{user_astronaut.astronaut} is ready to new missions"
                )
                user_astronaut.save()
            current_user.save()
            user_mission.save()

    add_missions = request.POST.get("add_missions")
    if add_missions == "1":
        missions = Mission.objects.all()
        for mission in missions:
            user_mission = UserMission()
            user_mission.mission = mission
            user_mission.user = current_user
            user_mission.save()

    add_astronauts = request.POST.get("add_astronauts")
    if add_astronauts == "1":
        astronauts = Astronaut.objects.all()
        for astronaut in astronauts:
            user_astronaut = UserAstronaut()
            user_astronaut.astronaut = astronaut
            user_astronaut.user = current_user
            user_astronaut.save()

    profile = get_profile()
    events = UserEvent.objects.filter(user__pk=current_user.pk).order_by("-week", "-day", "-time")

    return render(request, "moonhr/home.html", {"profile": profile, "events": events})


def get_profile():
    current_user = UserProfile.get_current()
    candidates = UserAstronaut.objects.filter(user__pk=current_user.pk).filter(
        status=ASTRONAUT_STATUS_CHOISES.CANDIDATE
    )
    ready = UserAstronaut.objects.filter(user__pk=current_user.pk).filter(status=ASTRONAUT_STATUS_CHOISES.READY)
    new_missions = UserMission.objects.filter(user__pk=current_user.pk).filter(status=MISSION_STATUS_CHOISES.NEW)
    current_missions = UserMission.objects.filter(user__pk=current_user.pk).filter(
        status=MISSION_STATUS_CHOISES.INPROGRESS
    )
    finished_missions = UserMission.objects.filter(user__pk=current_user.pk).filter(
        status=MISSION_STATUS_CHOISES.FINISHED
    )

    profile = {
        "current_user": current_user,
        "candidates": len(candidates),
        "ready": len(ready),
        "new_missions": len(new_missions),
        "current_missions": len(current_missions),
        "finished_missions": len(finished_missions),
    }
    return profile


def finish_missions():
    current_user = UserProfile.get_current()
    mission_list = MissionListView()
    user_missions = mission_list.get_inprogress_missions()
    for user_mission in user_missions:
        user_mission.weeks_to_end = 0
        user_mission.change_status(
            MISSION_STATUS_CHOISES.FINISHED,
            f"{user_mission.user_astronaut.astronaut} finished mission in {user_mission.mission.place}",
        )
        current_user.score += user_mission.result.score
        current_user.save()
        user_mission.save()

    user_astronauts = UserAstronaut.objects.filter(user__pk=current_user.pk).filter(
        status=ASTRONAUT_STATUS_CHOISES.ONMISSION
    )
    for user_astronaut in user_astronauts:
        user_astronaut.change_status(
            ASTRONAUT_STATUS_CHOISES.READY, f"{user_astronaut.astronaut} is ready to new missions"
        )
        user_astronaut.save()


def reset_missions(missions):
    for mission in missions:
        mission.result = None
        mission.user_astronaut = None
        mission.status = MISSION_STATUS_CHOISES.NEW
        mission.weeks_to_end = UserMission.DEFAULT_WEEKS_TO_END
        mission.save()


def candidates_view(request):
    current_user = UserProfile.get_current()

    if current_user.time < UserProfile.TIME_DAY_END:
        hire_astronaut(request)

    current_user = UserProfile.get_current()
    message = f"Current time: {current_user.time}: 00."
    if current_user.time < UserProfile.TIME_DAY_END:
        message += " You can hire astronauts."
    else:
        message += " Day time is over. You can't hire more today."

    contac_list = ContactListView()
    paginator = Paginator(contac_list.get_candidates(), contac_list.paginate_by)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request, "moonhr/candidates.html", {"page_obj": page_obj, "message": message, "profile": get_profile()}
    )


def hire_astronaut(request):
    to_hire_pk = request.GET.get("contact_pk_to_hire")
    if to_hire_pk:
        current_user = UserProfile.get_current()
        current_user.do_work()
        user_astronaut = UserAstronaut.objects.get(pk=to_hire_pk)
        user_astronaut.change_status(ASTRONAUT_STATUS_CHOISES.READY, f"{user_astronaut.astronaut} joined ETCA")
        user_astronaut.save()


def employees_view(request):
    contact_list = ContactListView()
    paginator = Paginator(contact_list.get_employees(), contact_list.paginate_by)

    current_user = UserProfile.get_current()
    user_missions = UserMission.objects.filter(user__pk=current_user.pk).filter(status=MISSION_STATUS_CHOISES.NEW)

    send_to_mission(request, user_missions)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "moonhr/employees.html",
        {"page_obj": page_obj, "user_missions": user_missions, "profile": get_profile()},
    )


def send_to_mission(request, user_missions):
    user_astornaut_pk = request.POST.get("user_astornaut_pk")
    user_mission_pk = request.POST.get("user_mission_pk")

    if None not in (user_astornaut_pk, user_mission_pk):
        current_user = UserProfile.get_current()
        current_user.time += UserProfile.HOURS_PER_ACTION
        current_user.save()

        user_mission = user_missions.get(pk=user_mission_pk)

        user_astronaut = UserAstronaut.objects.get(pk=user_astornaut_pk)
        user_astronaut.status = ASTRONAUT_STATUS_CHOISES.ONMISSION
        user_mission.user_astronaut = user_astronaut

        user_mission.change_status(
            MISSION_STATUS_CHOISES.INPROGRESS,
            f"{user_mission.user_astronaut.astronaut} started mission in {user_mission.mission.place}",
        )

        astronaut_skills = AstronautSkill.objects.filter(astronaut__pk=user_mission.user_astronaut.astronaut.pk)
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
    remove_tag(request)

    user_astronaut_tags = UserAstronautTag.objects.filter(user_astronaut__pk=user_astronaut.pk)
    more_tags = list(Skill.objects.all())
    used_tags = []
    for user_astronaut_tag in user_astronaut_tags:
        used_tags.append(user_astronaut_tag.tag)
        more_tags.remove(user_astronaut_tag.tag)

    tags_menu_obj = {"user_astronaut_tags": user_astronaut_tags, "more_tags": more_tags}
    profile = get_profile()
    return render(
        request,
        "moonhr/cv.html",
        {"user_astronaut": user_astronaut, "tags_menu_obj": tags_menu_obj, "profile": profile},
    )


def add_tag(request, user_astronaut):
    add_tag_pk = request.GET.get("add_tag_pk")
    if add_tag_pk:
        skill_tag_to_add = Skill.objects.get(pk=add_tag_pk)
        user_astronaut_tag = UserAstronautTag()
        user_astronaut_tag.user_astronaut = user_astronaut
        user_astronaut_tag.tag = skill_tag_to_add
        user_astronaut_tag.save()


def remove_tag(request):
    remove_tag_pk = request.GET.get("remove_tag_pk")
    if remove_tag_pk:
        UserAstronautTag.objects.get(pk=remove_tag_pk).delete()


def missions_view(request):
    contact_list = ContactListView()
    current_user = UserProfile.get_current()
    user_missions = UserMission.objects.filter(user__pk=current_user.pk).filter(status=MISSION_STATUS_CHOISES.NEW)

    if current_user.time < UserProfile.TIME_DAY_END:
        send_to_mission(request, user_missions)

    mission_list = MissionListView()
    paginator = Paginator(mission_list.get_new_missions(), mission_list.paginate_by)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    user_astronauts = contact_list.get_ready()

    current_user = UserProfile.get_current()
    message = f"Current time: {current_user.time}:00."
    if current_user.time < UserProfile.TIME_DAY_END:
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
            "profile": get_profile(),
        },
    )


class MissionWithDescription:
    def __init__(self, user_mission, description):
        self.user_mission = user_mission
        self.description = description


def workon_missions_view(request):
    mission_list = MissionListView()
    type_of_mission = request.GET.get("type")
    if type_of_mission == "finished":
        missions = mission_list.get_finished_missions()
    else:
        missions = mission_list.get_inprogress_missions()

    missions_with_description = []
    for mission in missions:
        description = mission.correct_description()
        missions_with_description.append(MissionWithDescription(mission, description))

    paginator = Paginator(missions_with_description, mission_list.paginate_by)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "moonhr/workon-missions.html",
        {
            "page_obj": page_obj,
            "finished": type_of_mission == "finished",
            "profile": get_profile(),
        },
    )


def mission_description_view(request):
    to_view_pk = request.GET.get("mission_pk_to_view")
    current_user = UserProfile.get_current()
    mission = UserMission.objects.filter(user__pk=current_user.pk).get(pk=to_view_pk)

    description = mission.correct_description()

    return render(
        request,
        "moonhr/mission-description.html",
        {"page_obj": mission, "description": description, "profile": get_profile()},
    )
