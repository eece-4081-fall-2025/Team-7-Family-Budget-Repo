from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.shortcuts import redirect
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


class ProfileContextMixin(LoginRequiredMixin):
    _profile = None

    def get_profile(self):
        if self._profile is None:
            self._profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return self._profile


class GroupJoinView(ProfileContextMixin, FormView):
    template_name = "budget/group_join.html"
    form_class = GroupJoinForm
    success_url = reverse_lazy("group_members")

    def form_valid(self, form):
        profile = self.get_profile()
        if profile.group_id:
            form.add_error(
                None,
                "You are already in a family group. Leave it before joining another.",
            )
            return self.form_invalid(form)
        group = FamilyGroup.objects.get(code=form.cleaned_data["code"])
        profile.group = group
        profile.save()
        return super().form_valid(form)


class GroupCreateView(ProfileContextMixin, CreateView):
    template_name = "budget/group_create.html"
    form_class = GroupCreateForm
    success_url = reverse_lazy("group_members")

    def form_valid(self, form):
        profile = self.get_profile()
        if profile.group_id:
            form.add_error(
                None,
                "You are already in a family group. Leave it before creating another.",
            )
            return self.form_invalid(form)
        group = form.save(commit=False)
        group.owner = self.request.user
        group.save()
        profile.group = group
        profile.save()
        return super().form_valid(form)


class GroupMembersView(ProfileContextMixin, TemplateView):
    template_name = "budget/group_members.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile = self.get_profile()
        group = profile.group
        if group:
            users = group.members_qs()
            members = [
                {
                    "username": u.username,
                    "role": group.role_of(u),
                    "income": getattr(u.profile, "income", 0),
                    "expenses": getattr(u.profile, "expenses", 0),
                }
                for u in users
            ]
        else:
            members = []
        ctx["group"] = group
        ctx["members"] = members
        return ctx


class GroupLeaveView(ProfileContextMixin, View):
    success_url = reverse_lazy("group_members")

    def post(self, request, *args, **kwargs):
        profile = self.get_profile()
        profile.group = None
        profile.save()
        return redirect(self.success_url)
