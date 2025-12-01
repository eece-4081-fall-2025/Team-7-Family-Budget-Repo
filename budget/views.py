# budget/views.py

from django.contrib.auth import get_user_model, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, FormView

from .forms import ProfileForm
from .forms_group import GroupJoinForm
from .models import Profile, FamilyGroup
from . import services

User = get_user_model()


class HomeView(TemplateView):
    template_name = "budget/home.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "budget/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile = services.get_profile(self.request.user)
        group = profile.group
        ctx["profile"] = profile
        ctx["group"] = group
        # Owner is the User on the FamilyGroup
        ctx["is_owner"] = bool(group and group.owner == self.request.user)
        return ctx


class SignupView(CreateView):
    template_name = "budget/signup.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("login")


class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = "budget/profile_form.html"
    form_class = ProfileForm
    success_url = reverse_lazy("budget_dashboard")

    def get_object(self, queryset=None):
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

        code = form.cleaned_data["code"]
        try:
            group = FamilyGroup.objects.get(code=code)
        except FamilyGroup.DoesNotExist:
            form.add_error("code", "No family group found with that code.")
            return self.form_invalid(form)

        services.attach_profile_to_group(profile, group)
        return super().form_valid(form)


class GroupCreateView(LoginRequiredMixin, CreateView):
    model = FamilyGroup
    fields = ["name"]
    template_name = "budget/group_create.html"
    success_url = reverse_lazy("group_members")

    def form_valid(self, form):
        profile = services.get_profile(self.request.user)

        if not services.can_join_or_create_group(profile):
            form.add_error(None, "You are already in a family group.")
            return self.form_invalid(form)

        # Owner is the User
        form.instance.owner = self.request.user
        response = super().form_valid(form)

        # Attach the creator to the group as a member
        services.attach_profile_to_group(profile, self.object)
        return response


class GroupMembersView(LoginRequiredMixin, TemplateView):
    template_name = "budget/group_members.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile = services.get_profile(self.request.user)
        group = profile.group
        ctx["group"] = group
        ctx["is_owner"] = bool(group and group.owner == self.request.user)

        if group is not None:
            # Returns dicts: profile_id, username, display_name, role, income, expenses
            members = services.build_members_list(group)
        else:
            members = []

        ctx["members"] = members
        return ctx


class GroupLeaveView(LoginRequiredMixin, View):
    """
    Let the current user leave their family group.
    """

    def post(self, request, *args, **kwargs):
        profile = services.get_profile(request.user)
        if profile.group is not None:
            profile.group = None
            profile.save()
        return redirect("group_members")


class ConfirmLogoutView(LoginRequiredMixin, View):
    template_name = "registration/logout_confirm.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        if "confirm" in request.POST:
            logout(request)
            return redirect("budget_home")
        return redirect("budget_dashboard")


class AdminManageMembersView(LoginRequiredMixin, TemplateView):
    """
    Owner-only page to add/remove members by username or profile id.
    """

    template_name = "budget/admin_manage_members.html"

    def _get_profile_and_group(self, user):
        """
        Get the Profile for this user, and the FamilyGroup they belong to
        or own.

        - First check profile.group
        - If that's None, fall back to any FamilyGroup where owner == user
        """
        profile = services.get_profile(user)
        group = profile.group

        if group is None:
            group = FamilyGroup.objects.filter(owner=user).first()

        return profile, group

    def dispatch(self, request, *args, **kwargs):
        """
        Redirect non-owners back to the members page.
        """
        profile, group = self._get_profile_and_group(request.user)
        if not group or group.owner != request.user:
            return redirect("group_members")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile, group = self._get_profile_and_group(self.request.user)

        members = services.build_members_list(group) if group else []
        ctx["group"] = group
        ctx["members"] = members
        ctx["error"] = getattr(self, "_error", "")
        return ctx

    def post(self, request, *args, **kwargs):
        """
        Handles both:
        - action == "add": add by username
        - action == "remove": remove member by profile id
        """
        profile, group = self._get_profile_and_group(request.user)

        # Only the owner of the group may make changes
        if not group or group.owner != request.user:
            return redirect("group_members")

        action = request.POST.get("action", "").strip()

        # ADD MEMBER BY USERNAME
        if action == "add":
            username = request.POST.get("username", "").strip()
            if not username:
                self._error = "Please provide a username."
            else:
                try:
                    user_to_add = User.objects.get(username=username)
                except User.DoesNotExist:
                    self._error = "User not found."
                else:
                    profile_to_add = services.get_profile(user_to_add)
                    services.attach_profile_to_group(profile_to_add, group)

        # REMOVE MEMBER BY PROFILE ID
        elif action == "remove":
            member_profile_id = request.POST.get("member_profile_id")
            if member_profile_id:
                member_profile = get_object_or_404(
                    Profile, pk=member_profile_id, group=group
                )
                # Do not allow the owner to remove themselves here
                if member_profile.user != request.user:
                    member_profile.group = None
                    member_profile.save()

        return redirect("group_manage_members")


class AdminRemoveMemberView(LoginRequiredMixin, View):
    """
    Optional extra endpoint to remove a member via /group/remove-member/<profile_id>/.
    Not required by the tests, but safe to keep.
    """

    def post(self, request, profile_id, *args, **kwargs):
        current_profile, group = AdminManageMembersView()._get_profile_and_group(
            request.user
        )

        # Only the owner can remove members
        if not group or group.owner != request.user:
            return redirect("group_members")

        member_profile = get_object_or_404(Profile, pk=profile_id, group=group)

        # Do not allow the owner to remove themselves
        if member_profile.user != request.user:
            member_profile.group = None
            member_profile.save()

        return redirect("group_manage_members")
