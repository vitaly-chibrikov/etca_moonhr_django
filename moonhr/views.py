from django.core.paginator import Paginator
from django.shortcuts import render
from moonhr.models import *
from django.views.generic import ListView

PAGINATE_BY_CONST = 5

class ContactListView(ListView):
    paginate_by = PAGINATE_BY_CONST

    def __init__(self):
        self.currentUser = UserProfile.objects.get(isSelected=True)

    def getCandidates(self):
        astronauts = UserAstronaut.objects.filter(user__pk=self.currentUser.pk).filter(status='candidate')
        return astronauts

    def getEmployees(self):
        astronauts = UserAstronaut.objects.filter(user__pk=self.currentUser.pk).exclude(status='candidate')
        return astronauts


def homeView(request):
    return render(request, "moonhr/home.html")

def candidatesView(request):
    contacList = ContactListView()
    paginator = Paginator(contacList.getCandidates(),
                          contacList.paginate_by)

    to_hire_pk = request.GET.get("contact_pk_to_hire")
    if(to_hire_pk):
        userAstronaut = UserAstronaut.objects.get(pk=to_hire_pk)
        userAstronaut.status = "ready"
        userAstronaut.save()

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "moonhr/candidates.html", {"page_obj": page_obj})


def employeesView(request):
    contact_list = ContactListView()
    paginator = Paginator(contact_list.getEmployees(),
                          contact_list.paginate_by)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "moonhr/employees.html", {"page_obj": page_obj})

def cvView(request):
    to_view_pk = request.GET.get("contact_pk_to_view")
    currentUser = UserProfile.objects.get(isSelected=True)
    astronaut = UserAstronaut.objects.filter(user__pk=currentUser.pk).get(pk=to_view_pk)
    return render(request, "moonhr/cv.html", {"page_obj": astronaut})
