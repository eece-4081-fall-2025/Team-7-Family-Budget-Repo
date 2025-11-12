from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .forms import ProfileForm
from .forms_group import GroupJoinForm, GroupCreateForm
from .models import Profile, FamilyGroup
from . import services

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
        return services.get_profile(self.request.user)


class GroupJoinView(LoginRequiredMixin, FormView):
    template_name = "budget/group_join.html"
    form_class = GroupJoinForm
    success_url = reverse_lazy("group_members")

    def form_valid(self, form):
        profile = services.get_profile(self.request.user)
        if not services.can_join_or_create_group(profile):
            form.add_error(
                None,
                "You are already in a family group. Leave it before joining another.",
            )
            return self.form_invalid(form)
        group = FamilyGroup.objects.get(code=form.cleaned_data["code"])
        services.attach_profile_to_group(profile, group)
        return super().form_valid(form)


class GroupCreateView(LoginRequiredMixin, CreateView):
    template_name = "budget/group_create.html"
    form_class = GroupCreateForm
    success_url = reverse_lazy("group_members")

    def form_valid(self, form):
        profile = services.get_profile(self.request.user)
        if not services.can_join_or_create_group(profile):
            form.add_error(
                None,
                "You are already in a family group. Leave it before creating another.",
            )
            return self.form_invalid(form)
        group = form.save(commit=False)
        group.owner = self.request.user
        group.save()
        services.attach_profile_to_group(profile, group)
        return super().form_valid(form)


class GroupMembersView(LoginRequiredMixin, TemplateView):
    template_name = "budget/group_members.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile = services.get_profile(self.request.user)
        group = profile.group
        if group is not None:
            members = services.build_members_list(group)
        else:
            members = []
        ctx["group"] = group
        ctx["members"] = members
        return ctx


class GroupLeaveView(LoginRequiredMixin, View):
    success_url = reverse_lazy("group_members")

    def post(self, request, *args, **kwargs):
        profile = services.get_profile(request.user)
        services.detach_profile_from_group(profile)
        return redirect(self.success_url)
