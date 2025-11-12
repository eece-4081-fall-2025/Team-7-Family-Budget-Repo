from django.views.generic import TemplateView, CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from .forms import ProfileForm
from .forms_group import GroupJoinForm, GroupCreateForm
from .models import Profile, FamilyGroup

User = get_user_model()


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


class GroupJoinView(LoginRequiredMixin, FormView):
    template_name = "budget/group_join.html"
    form_class = GroupJoinForm
    success_url = reverse_lazy("group_members")

    def form_valid(self, form):
        group = FamilyGroup.objects.get(code=form.cleaned_data["code"])
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        profile.group = group
        profile.save()
        return super().form_valid(form)


class GroupCreateView(LoginRequiredMixin, CreateView):
    template_name = "budget/group_create.html"
    form_class = GroupCreateForm
    success_url = reverse_lazy("group_members")

    def form_valid(self, form):
        group = form.save(commit=False)
        group.owner = self.request.user
        group.save()
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        profile.group = group
        profile.save()
        return super().form_valid(form)


class GroupMembersView(LoginRequiredMixin, TemplateView):
    template_name = "budget/group_members.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        group = profile.group
        members = []
        if group:
            qs = User.objects.filter(profile__group=group).select_related()
            members = [
                {
                    "username": u.username,
                    "role": "Admin" if group.owner_id == u.id else "Member",
                    "income": getattr(u.profile, "income", 0),
                    "expenses": getattr(u.profile, "expenses", 0),
                }
                for u in qs
            ]
        ctx["group"] = group
        ctx["members"] = members
        return ctx
