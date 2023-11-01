from django.contrib import admin
from moonhr.models import *


class AstronautAdmin(admin.ModelAdmin):
    list_display = ('name', 'cv')
admin.site.register(Astronaut, AstronautAdmin)


class SkillDescriptionAdmin(admin.ModelAdmin):
    list_display = ('skillName', 'skillDesc')
admin.site.register(SkillDescription, SkillDescriptionAdmin)

class MissionRequestParametersAdmin(admin.ModelAdmin):
    pass
admin.site.register(MissionRequestParameters, MissionRequestParametersAdmin)

admin.site.register(MissionDebriefing)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('userName', 'isSelected')
admin.site.register(UserProfile, UserProfileAdmin)

admin.site.register(UserAstronaut)