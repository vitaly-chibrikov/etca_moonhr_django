from django.urls import path
from moonhr import views

urlpatterns = [
    path("", views.homeView),
    path("candidates/", views.candidatesView),
    path("employees/", views.employeesView),
]