from django.urls import path
from moonhr import views

urlpatterns = [
    path("", views.home_view),
    path("candidates/", views.candidates_view),
    path("employees/", views.employees_view),
    path("cv/", views.cv_view),
    path("missions/", views.missions_view), 
    path("workon-missions/", views.workon_missions_view),   
    path("mission-description/", views.mission_description_view),       
]