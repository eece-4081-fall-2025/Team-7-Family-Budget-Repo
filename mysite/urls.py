from django.contrib import admin
from django.urls import path, include

from budget.views import (
    HomeView,
    DashboardView,
    SignupView,
    ProfileEditView,
    ConfirmLogoutView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("budget.urls")),
    path("signup/", SignupView.as_view(), name="signup"),
    path("profile/edit/", ProfileEditView.as_view(), name="profile_edit"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("logout/confirm/", ConfirmLogoutView.as_view(), name="logout_confirm"),
    path("", HomeView.as_view(), name="home"),
]
