from django.core.paginator import Paginator
from django.shortcuts import render
from moonhr.models import *
from django.views.generic import ListView


class ContactListView(ListView):
    paginate_by = 5
    userAstornautModel = UserAstronaut
    userProfileModel = UserProfile

    def getCandidates(self):
        currentUser = self.userProfileModel.objects.get(pk=1)
        astronauts = self.userAstornautModel.objects.filter(status='candidate').filter(user__pk=currentUser.pk)
        return astronauts

    def getEmployees(self):
        astronauts = self.userAstornautModel.objects.exclude(
            status='candidate')
        return astronauts


def homeView(request):
    return render(request, "moonhr/home.html")


def candidatesView(request):
    contact_list = ContactListView()
    paginator = Paginator(contact_list.getCandidates(),
                          contact_list.paginate_by)

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
