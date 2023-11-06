from django.urls import path
from moonhr import views

urlpatterns = [
    path("", views.home_view),
    path("candidates/", views.candidates_view),
    path("employees/", views.employees_view),
    path("cv/", views.cv_view),
    path("missions/", views.missions_view), 
    path("finished-missions/", views.finished_missions_view),   
    path("mission-description/", views.mission_description_view),       
]