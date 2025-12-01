
from decimal import Decimal, InvalidOperation

from django.contrib.auth import get_user_model, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, FormView

from . import services
from .forms import ProfileForm
from .forms_group import GroupJoinForm
from .models import Profile, FamilyGroup, Category, Goal

User = get_user_model()


class HomeView(TemplateView):
    template_name = "budget/home.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "budget/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = services.get_profile(self.request.user)
        group = profile.group

        context["profile"] = profile
        context["group"] = group
        context["is_owner"] = bool(group and group.owner == self.request.user)

        return context


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

    def form_valid(self, form):
        response = super().form_valid(form)

        profile = self.object
        group = profile.group
        if not group:
            return response

        total_extra = Decimal("0")

        for category in Category.objects.filter(group=group):
            field_name = f"category_expense_{category.id}"
            raw = self.request.POST.get(field_name, "").strip()
            if not raw:
                continue

            try:
                amount = Decimal(raw)
            except InvalidOperation:
                amount = None

            if amount is not None and amount > 0:
                total_extra += amount

        if total_extra:
            current = profile.expenses or Decimal("0")
            profile.expenses = current + total_extra
            profile.save(update_fields=["expenses"])

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        group = profile.group
        context["categories"] = (
            Category.objects.filter(group=group).order_by("name") if group else []
        )
        return context


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
        profile.is_admin = False
        profile.save()

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

        form.instance.owner = self.request.user
        response = super().form_valid(form)

        services.attach_profile_to_group(profile, self.object)
        profile.is_admin = False
        profile.save()

        return response


class GroupMembersView(LoginRequiredMixin, TemplateView):
    template_name = "budget/group_members.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = services.get_profile(self.request.user)
        group = profile.group

        if group is not None:
            members = services.build_members_list(group)
            categories = Category.objects.filter(group=group).order_by("name")
            goals = Goal.objects.filter(group=group).order_by("created_at")
        else:
            members = []
            categories = []
            goals = []

        context["group"] = group
        context["members"] = members
        context["categories"] = categories
        context["goals"] = goals
        context["is_owner"] = bool(group and group.owner == self.request.user)

        return context



class GroupLeaveView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        profile = services.get_profile(request.user)
        if profile.group is not None:
            profile.group = None
            profile.is_admin = False
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
    template_name = "budget/admin_manage_members.html"

    def _get_profile_and_group(self, user):
        profile = services.get_profile(user)
        group = profile.group

        if group is None:
            group = FamilyGroup.objects.filter(owner=user).first()

        return profile, group

    def dispatch(self, request, *args, **kwargs):
        profile, group = self._get_profile_and_group(request.user)
        if not group or group.owner != request.user:
            return redirect("group_members")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, group = self._get_profile_and_group(self.request.user)

        members = services.build_members_list(group) if group else []
        context["group"] = group
        context["members"] = members
        context["error"] = getattr(self, "_error", "")

        return context

    def post(self, request, *args, **kwargs):
        profile, group = self._get_profile_and_group(request.user)

        if not group or group.owner != request.user:
            return redirect("group_members")

        action = request.POST.get("action", "").strip()

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
                    profile_to_add.is_admin = False
                    profile_to_add.save()

        elif action == "remove":
            member_profile_id = request.POST.get("member_profile_id")
            if member_profile_id:
                member_profile = get_object_or_404(
                    Profile, pk=member_profile_id, group=group
                )
                if member_profile.user != request.user:
                    member_profile.group = None
                    member_profile.is_admin = False
                    member_profile.save()

        elif action in {"promote", "demote"}:
            member_profile_id = request.POST.get("member_profile_id")
            if member_profile_id:
                member_profile = get_object_or_404(
                    Profile, pk=member_profile_id, group=group
                )
                if (
                    member_profile.user != request.user
                    and member_profile.user != group.owner
                ):
                    member_profile.is_admin = action == "promote"
                    member_profile.save()

        return redirect("group_manage_members")


class AdminRemoveMemberView(LoginRequiredMixin, View):
    def post(self, request, profile_id, *args, **kwargs):
        current_profile, group = AdminManageMembersView()._get_profile_and_group(
            request.user
        )

        if not group or group.owner != request.user:
            return redirect("group_members")

        member_profile = get_object_or_404(Profile, pk=profile_id, group=group)

        if member_profile.user != request.user:
            member_profile.group = None
            member_profile.save()

        return redirect("group_manage_members")


class CategoryManageView(LoginRequiredMixin, TemplateView):
    template_name = "budget/category_manage.html"

    def dispatch(self, request, *args, **kwargs):
        profile = services.get_profile(request.user)
        group = profile.group

        if not group or (group.owner != request.user and not profile.is_admin):
            return HttpResponseForbidden(
                "Only the group owner or an admin can manage categories."
            )

        self.group = group
        self.profile = profile
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = self.group
        context["categories"] = Category.objects.filter(
            group=self.group
        ).order_by("name")
        return context

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name", "").strip()
        if name:
            Category.objects.get_or_create(group=self.group, name=name)

        category_id = request.POST.get("category_id", "").strip()
        limit_raw = request.POST.get("limit", "").strip()
        if category_id and limit_raw:
            try:
                category = Category.objects.get(id=category_id, group=self.group)
                category.budget_limit = Decimal(limit_raw)
                category.save()
            except (Category.DoesNotExist, ValueError, InvalidOperation):
                pass

        delete_id = request.POST.get("delete_category_id", "").strip()
        if delete_id:
            try:
                category_to_delete = Category.objects.get(id=delete_id, group=self.group)
                category_to_delete.delete()
            except Category.DoesNotExist:
                pass

        return redirect("category_manage")


class GoalManageView(LoginRequiredMixin, TemplateView):
    template_name = "budget/goals_manage.html"

    def dispatch(self, request, *args, **kwargs):
        profile = services.get_profile(request.user)
        group = profile.group

        if not group or (group.owner != request.user and not profile.is_admin):
            return HttpResponseForbidden(
                "Only the group owner or an admin can manage goals."
            )

        self.group = group
        self.profile = profile
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = self.group
        context["goals"] = Goal.objects.filter(
            group=self.group
        ).order_by("created_at")
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action", "create")

        if action == "delete":
            goal_id = request.POST.get("goal_id")
            if goal_id:
                Goal.objects.filter(id=goal_id, group=self.group).delete()
            return redirect("goal_manage")

        name = request.POST.get("name", "").strip()
        target_raw = request.POST.get("target_amount", "").strip()

        if name and target_raw:
            try:
                target = Decimal(target_raw)
            except InvalidOperation:
                target = None

            if target is not None:
                Goal.objects.create(
                    group=self.group,
                    name=name,
                    target_amount=target,
                )

        return redirect("goal_manage")
