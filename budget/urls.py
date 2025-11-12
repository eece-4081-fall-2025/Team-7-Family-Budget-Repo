from django.urls import path
from .views import (
    HomeView,
    DashboardView,
    SignupView,
    ProfileEditView,
    GroupJoinView,
    GroupCreateView,
    GroupMembersView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="budget_home"),
    path("dashboard/", DashboardView.as_view(), name="budget_dashboard"),
    path("signup/", SignupView.as_view(), name="budget_signup"),
    path("profile/edit/", ProfileEditView.as_view(), name="profile_edit"),
    path("group/join/", GroupJoinView.as_view(), name="group_join"),
    path("group/create/", GroupCreateView.as_view(), name="group_create"),
    path("group/members/", GroupMembersView.as_view(), name="group_members"),
]
