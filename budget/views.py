from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .forms import ProfileForm
from .models import Profile


class HomeView(TemplateView):
    template_name = "budget/home.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "budget/dashboard.html"


class SignupView(CreateView):
    template_name = "budget/signup.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("login")


class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = "budget/profile_form.html"
    form_class = ProfileForm
    success_url = reverse_lazy("budget_dashboard")

    def get_object(self):
        obj, _ = Profile.objects.get_or_create(user=self.request.user)
        return obj
