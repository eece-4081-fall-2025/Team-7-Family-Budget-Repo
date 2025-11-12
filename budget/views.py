from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required


class SignupView(CreateView):
    template_name = "budget/signup.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("login")


def home(request):
    return render(request, "budget/home.html")


@login_required(login_url="/accounts/login/")
def dashboard(request):
    return render(request, "budget/dashboard.html")
