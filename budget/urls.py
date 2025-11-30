from django.urls import path
from .views import (
    HomeView,
    SignupView,
    DashboardView,
    ProfileEditView,
    GroupCreateView,
    GroupJoinView,
    GroupMembersView,
    LogoutConfirmView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="budget_home"),
    path("signup/", SignupView.as_view(), name="budget_signup"),
    path("dashboard/", DashboardView.as_view(), name="budget_dashboard"),
    path("profile/edit/", ProfileEditView.as_view(), name="profile_edit"),
    path("group/create/", GroupCreateView.as_view(), name="group_create"),
    path("group/join/", GroupJoinView.as_view(), name="group_join"),
    path("group/members/", GroupMembersView.as_view(), name="group_members"),
    path("logout/confirm/", LogoutConfirmView.as_view(), name="budget_logout_confirm"),
]
