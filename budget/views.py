from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ProfileForm
from .models import Profile


class SignupView(CreateView):
    template_name = "budget/signup.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("login")


def home(request):
    return render(request, "budget/home.html")


@login_required(login_url="/accounts/login/")
def dashboard(request):
    return render(request, "budget/dashboard.html")


class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = "budget/profile_form.html"
    form_class = ProfileForm
    success_url = reverse_lazy("budget_dashboard")

    def get_object(self):
        obj, _ = Profile.objects.get_or_create(user=self.request.user)
        return obj
