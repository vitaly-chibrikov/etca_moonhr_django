from django.contrib import admin
from moonhr.models import *


class AstronautAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'sex')
admin.site.register(Astronaut, AstronautAdmin)


class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc')
admin.site.register(Skill, SkillAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'is_selected')
admin.site.register(UserProfile, UserProfileAdmin)

admin.site.register(UserAstronaut)

admin.site.register(AstronautSkill)

admin.site.register(Mission)

admin.site.register(MissionSkillResult)

admin.site.register(MissionResult)

admin.site.register(UserMission)

admin.site.register(Place)