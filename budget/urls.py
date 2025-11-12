from django.urls import path
from .views import HomeView, DashboardView, SignupView, ProfileEditView

urlpatterns = [
    path("", HomeView.as_view(), name="budget_home"),
    path("dashboard/", DashboardView.as_view(), name="budget_dashboard"),
    path("signup/", SignupView.as_view(), name="budget_signup"),
    path("profile/edit/", ProfileEditView.as_view(), name="profile_edit"),
]
