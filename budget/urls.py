# budget/urls.py

from django.urls import path

from .views import (
    HomeView,
    DashboardView,
    SignupView,
    ProfileEditView,
    GroupJoinView,
    GroupCreateView,
    GroupMembersView,
    GroupLeaveView,
    ConfirmLogoutView,
    AdminManageMembersView,
    AdminRemoveMemberView,
)

urlpatterns = [
    # Home & dashboard
    path("", HomeView.as_view(), name="budget_home"),
    path("dashboard/", DashboardView.as_view(), name="budget_dashboard"),

    # Auth / signup
    path("signup/", SignupView.as_view(), name="budget_signup"),

    # Profile editing
    path("profile/edit/", ProfileEditView.as_view(), name="profile_edit"),

    # Group join/create/members/leave
    path("group/join/", GroupJoinView.as_view(), name="group_join"),
    path("group/create/", GroupCreateView.as_view(), name="group_create"),
    path("group/members/", GroupMembersView.as_view(), name="group_members"),
    path("group/leave/", GroupLeaveView.as_view(), name="group_leave"),

    # Owner-only member management
    path(
        "group/manage-members/",
        AdminManageMembersView.as_view(),
        name="group_manage_members",
    ),
    path(
        "group/remove-member/<int:profile_id>/",
        AdminRemoveMemberView.as_view(),
        name="group_remove_member",
    ),

    # Logout confirmation
    path(
        "accounts/logout/confirm/",
        ConfirmLogoutView.as_view(),
        name="budget_logout_confirm",
    ),
]



